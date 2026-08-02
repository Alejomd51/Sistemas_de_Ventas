from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from productos.models import Categoria, Producto
from usuarios.models import Usuario

from .models import TASA_IVA, ItemVenta, Venta


class VentaModelTests(TestCase):
    def test_crear_venta_reduce_el_stock_del_producto(self):
        categoria = Categoria.objects.create(nombre="Lácteos")
        producto = Producto.objects.create(
            nombre="Leche",
            descripcion="Leche entera",
            precio=Decimal("1.75"),
            stock=20,
            categoria=categoria,
        )
        vendedor = Usuario.objects.create_user(
            username="vendedor",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )

        venta = Venta.objects.create(vendedor=vendedor)
        item = ItemVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=3,
            precio_unitario=producto.precio,
        )

        producto.refresh_from_db()
        self.assertEqual(item.subtotal, Decimal("5.25"))
        self.assertEqual(producto.stock, 17)
        self.assertEqual(venta.items.count(), 1)

    def test_venta_sin_vendedor_es_valida(self):
        venta = Venta.objects.create()
        self.assertIsNone(venta.vendedor)
        self.assertEqual(str(venta), f"Venta {venta.pk}")

    def test_calcular_totales_con_impuestos(self):
        """El método calcular_totales() calcula subtotal + IVA + total."""
        categoria = Categoria.objects.create(nombre="Test")
        producto = Producto.objects.create(
            nombre="Producto A",
            precio=Decimal("10.00"),
            stock=100,
            categoria=categoria,
        )

        venta = Venta.objects.create()
        item = ItemVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=2,
            precio_unitario=producto.precio,
        )

        venta.calcular_totales([item])

        # subtotal = 2 * 10.00 = 20.00
        self.assertEqual(venta.subtotal, Decimal("20.00"))
        # impuesto = 20.00 * 0.15 = 3.00
        expected_impuesto = (Decimal("20.00") * TASA_IVA).quantize(Decimal("0.01"))
        self.assertEqual(venta.impuesto, expected_impuesto)
        # total = subtotal + impuesto
        self.assertEqual(venta.total, venta.subtotal + venta.impuesto)

    def test_tasa_iva_porcentaje(self):
        venta = Venta()
        self.assertEqual(venta.tasa_iva_porcentaje, int(TASA_IVA * 100))

    def test_no_permite_crear_item_sin_stock(self):
        categoria = Categoria.objects.create(nombre="Stock limitado")
        producto = Producto.objects.create(
            nombre="Producto limitado",
            precio=Decimal("2.00"),
            stock=1,
            categoria=categoria,
        )
        venta = Venta.objects.create()

        with self.assertRaises(ValidationError):
            ItemVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=2,
                precio_unitario=producto.precio,
            )

        producto.refresh_from_db()
        self.assertEqual(producto.stock, 1)

    def test_editar_cantidad_ajusta_solo_la_diferencia(self):
        categoria = Categoria.objects.create(nombre="Edición stock")
        producto = Producto.objects.create(
            nombre="Producto editable",
            precio=Decimal("2.00"),
            stock=10,
            categoria=categoria,
        )
        venta = Venta.objects.create()
        item = ItemVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=2,
            precio_unitario=producto.precio,
        )

        item.cantidad = 5
        item.save()
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 5)

        item.cantidad = 1
        item.save()
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 9)

    def test_cambiar_producto_restaura_el_anterior(self):
        categoria = Categoria.objects.create(nombre="Cambio producto")
        anterior = Producto.objects.create(
            nombre="Producto anterior", precio=Decimal("1.00"), stock=10, categoria=categoria
        )
        nuevo = Producto.objects.create(
            nombre="Producto nuevo", precio=Decimal("2.00"), stock=8, categoria=categoria
        )
        venta = Venta.objects.create()
        item = ItemVenta.objects.create(
            venta=venta, producto=anterior, cantidad=3, precio_unitario=anterior.precio
        )

        item.producto = nuevo
        item.cantidad = 2
        item.precio_unitario = nuevo.precio
        item.save()

        anterior.refresh_from_db()
        nuevo.refresh_from_db()
        self.assertEqual(anterior.stock, 10)
        self.assertEqual(nuevo.stock, 6)

    def test_eliminar_item_restaura_stock(self):
        categoria = Categoria.objects.create(nombre="Eliminar item")
        producto = Producto.objects.create(
            nombre="Producto eliminable", precio=Decimal("3.00"), stock=10, categoria=categoria
        )
        venta = Venta.objects.create()
        item = ItemVenta.objects.create(
            venta=venta, producto=producto, cantidad=4, precio_unitario=producto.precio
        )

        item.delete()

        producto.refresh_from_db()
        self.assertEqual(producto.stock, 10)

    def test_eliminar_venta_restaura_stock_de_sus_items(self):
        categoria = Categoria.objects.create(nombre="Eliminar venta")
        producto = Producto.objects.create(
            nombre="Producto de venta", precio=Decimal("3.00"), stock=10, categoria=categoria
        )
        venta = Venta.objects.create()
        ItemVenta.objects.create(
            venta=venta, producto=producto, cantidad=4, precio_unitario=producto.precio
        )

        venta.delete()

        producto.refresh_from_db()
        self.assertEqual(producto.stock, 10)


def _formset_data(items, prefix="items"):
    """Construye el diccionario de datos del management form + ítems."""
    data = {
        f"{prefix}-TOTAL_FORMS": str(len(items)),
        f"{prefix}-INITIAL_FORMS": "0",
        f"{prefix}-MIN_NUM_FORMS": "1",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }
    for i, item in enumerate(items):
        for key, value in item.items():
            data[f"{prefix}-{i}-{key}"] = str(value)
    return data


class VentaViewTests(TestCase):
    def setUp(self):
        # Las migraciones incluyen ventas demostrativas; cada prueba de vistas
        # parte de un conjunto controlado para verificar únicamente sus datos.
        Venta.objects.all().delete()
        self.categoria = Categoria.objects.create(nombre="Lácteos")
        self.producto = Producto.objects.create(
            nombre="Leche",
            descripcion="Leche entera",
            precio=Decimal("1.75"),
            stock=20,
            categoria=self.categoria,
        )
        self.producto2 = Producto.objects.create(
            nombre="Yogur",
            descripcion="Yogur natural",
            precio=Decimal("2.50"),
            stock=15,
            categoria=self.categoria,
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        self.admin = Usuario.objects.create_user(
            username="admin-ventas",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.ADMIN,
        )

    def test_vendedor_puede_registrar_una_venta_con_impuestos(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 2},
        ])
        data["metodo_pago"] = "EFECTIVO"
        response = self.client.post(
            reverse("ventas:venta_crear"), data, follow=True,
        )

        self.producto.refresh_from_db()
        self.assertRedirects(response, reverse("ventas:ventas"))
        self.assertEqual(self.producto.stock, 18)
        self.assertContains(response, "Venta registrada correctamente")

        venta = Venta.objects.first()
        self.assertEqual(venta.items.count(), 1)

        # subtotal = 2 * 1.75 = 3.50
        self.assertEqual(venta.subtotal, Decimal("3.50"))
        # impuesto = 3.50 * 0.15 = 0.525 → 0.53 (redondeado)
        expected_impuesto = (Decimal("3.50") * TASA_IVA).quantize(Decimal("0.01"))
        self.assertEqual(venta.impuesto, expected_impuesto)
        # total = subtotal + impuesto
        self.assertEqual(venta.total, venta.subtotal + venta.impuesto)

    def test_venta_multiples_items_calcula_impuestos_correctamente(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 3},
            {"producto": self.producto2.pk, "cantidad": 2},
        ])
        data["metodo_pago"] = "EFECTIVO"
        response = self.client.post(
            reverse("ventas:venta_crear"), data, follow=True,
        )

        self.assertRedirects(response, reverse("ventas:ventas"))

        venta = Venta.objects.first()
        self.assertEqual(venta.items.count(), 2)

        self.producto.refresh_from_db()
        self.producto2.refresh_from_db()
        self.assertEqual(self.producto.stock, 17)   # 20 - 3
        self.assertEqual(self.producto2.stock, 13)  # 15 - 2

        # subtotal = (3 * 1.75) + (2 * 2.50) = 5.25 + 5.00 = 10.25
        self.assertEqual(venta.subtotal, Decimal("10.25"))
        expected_impuesto = (Decimal("10.25") * TASA_IVA).quantize(Decimal("0.01"))
        self.assertEqual(venta.impuesto, expected_impuesto)
        self.assertEqual(venta.total, venta.subtotal + venta.impuesto)

    def test_vendedor_puede_listar_ventas(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("ventas:ventas"))

        self.assertEqual(response.status_code, 200)

    def test_vendedor_solo_lista_sus_propias_ventas(self):
        otro_vendedor = Usuario.objects.create_user(
            username="otro-listado",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        venta_propia = Venta.objects.create(vendedor=self.vendedor)
        venta_ajena = Venta.objects.create(vendedor=otro_vendedor)
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("ventas:ventas"))

        self.assertQuerySetEqual(response.context["ventas"], [venta_propia])
        self.assertNotContains(response, f">{venta_ajena.pk}<")

    def test_admin_puede_listar_todas_las_ventas(self):
        otro_vendedor = Usuario.objects.create_user(
            username="otro-admin",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        Venta.objects.create(vendedor=self.vendedor)
        Venta.objects.create(vendedor=otro_vendedor)
        self.client.force_login(self.admin)

        response = self.client.get(reverse("ventas:ventas"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["ventas"].count(), 2)

    def test_admin_no_puede_registrar_ventas(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("ventas:venta_crear"))

        self.assertEqual(response.status_code, 403)

    def test_venta_asigna_vendedor_automaticamente(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 1},
        ])
        data["metodo_pago"] = "EFECTIVO"
        self.client.post(reverse("ventas:venta_crear"), data)

        venta = Venta.objects.first()
        self.assertEqual(venta.vendedor, self.vendedor)

    def test_venta_rechazada_si_stock_insuficiente(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 999},
        ])
        data["metodo_pago"] = "EFECTIVO"
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())

    def test_venta_rechazada_si_producto_duplicado(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 1},
            {"producto": self.producto.pk, "cantidad": 2},
        ])
        data["metodo_pago"] = "EFECTIVO"
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())
        self.assertContains(response, "duplicado")

    def test_venta_rechazada_sin_items(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([])
        data["metodo_pago"] = "EFECTIVO"
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())

    def test_lista_ventas_muestra_desglose_impuestos(self):
        """La lista de ventas muestra columnas de subtotal, IVA y total."""
        self.client.force_login(self.vendedor)

        # Crear una venta
        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 4},
        ])
        data["metodo_pago"] = "EFECTIVO"
        self.client.post(reverse("ventas:venta_crear"), data)

        response = self.client.get(reverse("ventas:ventas"))

        # Verificar que las columnas de desglose están presentes
        self.assertContains(response, "Subtotal")
        self.assertContains(response, "IVA")
        self.assertContains(response, "Total")
        # Verificar que hay datos de venta (el pk)
        venta = Venta.objects.first()
        self.assertContains(response, str(venta.pk))

    def test_vendedor_puede_ver_comprobante(self):
        self.client.force_login(self.vendedor)
        
        # Crear venta
        venta = Venta.objects.create(vendedor=self.vendedor)
        ItemVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1,
            precio_unitario=self.producto.precio
        )
        venta.calcular_totales()
        venta.save()
        
        response = self.client.get(reverse("ventas:venta_comprobante", args=[venta.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COMPROBANTE DE VENTA")
        self.assertContains(response, str(venta.pk))
        
    def test_vendedor_no_puede_ver_comprobante_de_otro_vendedor(self):
        otro_vendedor = Usuario.objects.create_user(
            username="otro",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        venta_otro = Venta.objects.create(vendedor=otro_vendedor)
        
        self.client.force_login(self.vendedor)
        response = self.client.get(reverse("ventas:venta_comprobante", args=[venta_otro.pk]))
        
        # Debe redirigir o prohibir
        self.assertRedirects(response, reverse("ventas:ventas"))

    def test_admin_puede_ver_cualquier_comprobante(self):
        venta = Venta.objects.create(vendedor=self.vendedor)
        self.client.force_login(self.admin)

        response = self.client.get(reverse("ventas:venta_comprobante", args=[venta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COMPROBANTE DE VENTA")
