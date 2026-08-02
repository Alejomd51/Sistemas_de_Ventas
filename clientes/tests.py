from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario
from ventas.models import Venta

from .models import Cliente


class ClienteViewsTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="vendedor-clientes",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        self.client.force_login(self.usuario)
        self.cliente = Cliente.objects.create(
            identificacion="1712345678",
            nombres="Ana",
            apellidos="Pérez",
            email="ana@example.com",
        )

    def test_lista_clientes_permite_buscar(self):
        response = self.client.get(reverse("clientes:lista"), {"q": "Ana"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana")

    def test_registro_rapido_crea_cliente(self):
        response = self.client.post(
            reverse("clientes:registro_rapido"),
            {
                "tipo_documento": "CEDULA",
                "identificacion": "1723456789",
                "nombres": "Luis",
                "apellidos": "Mora",
                "email": "luis@example.com",
                "telefono": "0999999999",
                "direccion": "Quito",
            },
        )

        self.assertRedirects(response, reverse("clientes:lista"))
        self.assertTrue(Cliente.objects.filter(identificacion="1723456789").exists())

    def test_historial_muestra_ventas_del_cliente(self):
        Venta.objects.create(
            vendedor=self.usuario,
            cliente=self.cliente,
            subtotal=Decimal("10.00"),
            impuesto=Decimal("1.50"),
            total=Decimal("11.50"),
        )

        response = self.client.get(reverse("clientes:historial", args=[self.cliente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "11,50")
        self.assertContains(response, "Total de compras: 1")

    def test_cliente_requiere_autenticacion(self):
        self.client.logout()

        response = self.client.get(reverse("clientes:lista"))

        self.assertRedirects(
            response,
            f'{reverse("usuarios:login")}?next={reverse("clientes:lista")}',
        )
