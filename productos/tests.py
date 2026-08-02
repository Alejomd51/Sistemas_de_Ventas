from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario

from .models import Categoria, Producto


class ProductosTests(TestCase):
    def test_crear_categoria_y_producto_con_relacion(self):
        categoria = Categoria.objects.create(nombre="Bebidas", descripcion="Refrescos")
        producto = Producto.objects.create(
            nombre="Gaseosa", descripcion="Botella de 1.5L", precio=2.5,
            stock=10, categoria=categoria,
        )

        self.assertEqual(producto.categoria, categoria)
        self.assertEqual(producto.stock, 10)
        self.assertTrue(producto.activo)


class CRUDProductosTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="administrador-productos",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.ADMIN,
        )
        self.categoria = Categoria.objects.create(
            nombre="Lácteos", descripcion="Productos lácteos"
        )

    def test_admin_puede_listar_productos(self):
        producto = Producto.objects.create(
            nombre="Leche", precio=1.75, stock=20, categoria=self.categoria
        )
        self.client.force_login(self.admin)

        response = self.client.get(reverse("productos:productos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, producto.nombre)

    def test_admin_puede_crear_producto(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("productos:producto_crear"),
            {
                "nombre": "Yogur", "descripcion": "Yogur natural",
                "precio": "2.50", "stock": "15",
                "categoria": self.categoria.pk, "activo": True,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("productos:productos"))
        self.assertTrue(Producto.objects.filter(nombre="Yogur").exists())

    def test_admin_puede_editar_producto(self):
        producto = Producto.objects.create(
            nombre="Leche", precio=1.75, stock=20, categoria=self.categoria
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("productos:producto_editar", kwargs={"pk": producto.pk}),
            {
                "nombre": "Leche desnatada", "descripcion": "Baja en grasa",
                "precio": "2.10", "stock": "10",
                "categoria": self.categoria.pk, "activo": True,
            },
            follow=True,
        )

        producto.refresh_from_db()
        self.assertRedirects(response, reverse("productos:productos"))
        self.assertEqual(producto.nombre, "Leche desnatada")

    def test_admin_puede_eliminar_producto(self):
        producto = Producto.objects.create(
            nombre="Queso", precio=3.5, stock=8, categoria=self.categoria
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("productos:producto_eliminar", kwargs={"pk": producto.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("productos:productos"))
        self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())

    def test_vendedor_no_puede_gestionar_productos(self):
        vendedor = Usuario.objects.create_user(
            username="vendedor-productos",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        self.client.force_login(vendedor)

        response = self.client.get(reverse("productos:productos"))

        self.assertEqual(response.status_code, 403)
