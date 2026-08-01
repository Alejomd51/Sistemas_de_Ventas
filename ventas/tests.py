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
        self.assertEqual(item.subtotal, 5.25)
        self.assertEqual(producto.stock, 17)
        self.assertEqual(venta.items.count(), 1)

    def test_venta_sin_vendedor_es_valida(self):
        venta = Venta.objects.create()
        self.assertIsNone(venta.vendedor)
        self.assertEqual(str(venta), f"Venta {venta.pk}")


class VentaViewTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Lácteos")
        self.producto = Producto.objects.create(
            nombre="Leche",
            descripcion="Leche entera",
            precio=1.75,
            stock=20,
            categoria=self.categoria,
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )

    def test_vendedor_puede_registrar_una_venta_desde_la_interfaz(self):
        self.client.force_login(self.vendedor)

        response = self.client.post(
            reverse("ventas:venta_crear"),
            {"producto": self.producto.pk, "cantidad": 2},
            follow=True,
        )

        self.producto.refresh_from_db()
        self.assertRedirects(response, reverse("ventas:ventas"))
        self.assertEqual(self.producto.stock, 18)
        self.assertContains(response, "Venta registrada correctamente")

    def test_vendedor_puede_listar_ventas(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("ventas:ventas"))

        self.assertEqual(response.status_code, 200)

    def test_venta_asigna_vendedor_automaticamente(self):
        self.client.force_login(self.vendedor)

        self.client.post(
            reverse("ventas:venta_crear"),
            {"producto": self.producto.pk, "cantidad": 1},
        )

        venta = Venta.objects.first()
        self.assertEqual(venta.vendedor, self.vendedor)

    def test_venta_rechazada_si_stock_insuficiente(self):
        self.client.force_login(self.vendedor)

        response = self.client.post(
            reverse("ventas:venta_crear"),
            {"producto": self.producto.pk, "cantidad": 999},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Venta.objects.exists())
