from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from productos.models import Categoria, Producto
from usuarios.models import Usuario
from ventas.models import ItemVenta, Venta


class ReportesTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="admin-reportes",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.ADMIN,
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor-reportes",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )
        categoria = Categoria.objects.create(nombre="Bebidas")
        self.producto = Producto.objects.create(
            nombre="Café",
            precio=Decimal("2.50"),
            stock=20,
            categoria=categoria,
        )
        self.venta = Venta.objects.create(
            vendedor=self.vendedor,
            subtotal=Decimal("5.00"),
            impuesto=Decimal("0.75"),
            total=Decimal("5.75"),
        )
        ItemVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal("2.50"),
        )

    def test_reporte_por_periodo_usa_campo_fecha(self):
        self.client.force_login(self.admin)
        hoy = timezone.localdate().isoformat()

        response = self.client.get(
            reverse("reportes:ventas_periodo"),
            {"fecha_inicio": hoy, "fecha_fin": hoy},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_transacciones"], 1)
        self.assertEqual(response.context["monto_total_periodo"], Decimal("5.75"))

    def test_productos_mas_vendidos_calcula_ingresos(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("reportes:top_productos"))

        self.assertEqual(response.status_code, 200)
        producto = response.context["top_productos"][0]
        self.assertEqual(producto["total_vendido"], 2)
        self.assertEqual(producto["ingresos"], Decimal("5"))

    def test_vendedor_no_puede_ver_reportes(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("reportes:ventas_periodo"))

        self.assertEqual(response.status_code, 403)

    def test_reportes_requieren_autenticacion(self):
        response = self.client.get(reverse("reportes:top_productos"))

        self.assertRedirects(
            response,
            f'{reverse("usuarios:login")}?next={reverse("reportes:top_productos")}',
        )
