from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from usuarios.models import Categoria, Producto, Usuario

from .models import ItemVenta, Venta


class VentaModelTests(TestCase):
    def test_crear_venta_reduce_el_stock_del_producto(self):
        categoria = Categoria.objects.create(nombre="Lácteos")
        producto = Producto.objects.create(
            nombre="Leche",
            descripcion="Leche entera",
            precio=1.75,
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

    def test_vendedor_puede_registrar_una_venta_con_un_item(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 2},
        ])
        response = self.client.post(
            reverse("ventas:venta_crear"), data, follow=True,
        )

        self.producto.refresh_from_db()
        self.assertRedirects(response, reverse("ventas:ventas"))
        self.assertEqual(self.producto.stock, 18)
        self.assertContains(response, "Venta registrada correctamente")

        venta = Venta.objects.first()
        self.assertEqual(venta.items.count(), 1)
        self.assertEqual(venta.total, Decimal("3.50"))

    def test_vendedor_puede_registrar_venta_con_multiples_items(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 3},
            {"producto": self.producto2.pk, "cantidad": 2},
        ])
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

        # Total: (3 * 1.75) + (2 * 2.50) = 5.25 + 5.00 = 10.25
        self.assertEqual(venta.total, Decimal("10.25"))

    def test_vendedor_puede_listar_ventas(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("ventas:ventas"))

        self.assertEqual(response.status_code, 200)

    def test_venta_asigna_vendedor_automaticamente(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 1},
        ])
        self.client.post(reverse("ventas:venta_crear"), data)

        venta = Venta.objects.first()
        self.assertEqual(venta.vendedor, self.vendedor)

    def test_venta_rechazada_si_stock_insuficiente(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 999},
        ])
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())

    def test_venta_rechazada_si_producto_duplicado(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([
            {"producto": self.producto.pk, "cantidad": 1},
            {"producto": self.producto.pk, "cantidad": 2},
        ])
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())
        self.assertContains(response, "duplicado")

    def test_venta_rechazada_sin_items(self):
        self.client.force_login(self.vendedor)

        data = _formset_data([])
        response = self.client.post(reverse("ventas:venta_crear"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())
