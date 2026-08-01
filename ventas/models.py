from decimal import Decimal

from django.conf import settings
from django.db import models


# Tasa de IVA configurable desde settings; por defecto 15 % (Ecuador).
TASA_IVA = Decimal(str(getattr(settings, "TASA_IVA", "0.15")))


class Venta(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta (Crédito/Débito)"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia Bancaria"

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ventas",
        verbose_name="vendedor",
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        verbose_name="método de pago"
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="fecha")
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="subtotal"
    )
    impuesto = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="impuesto (IVA)"
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="total"
    )

    class Meta:
        verbose_name = "venta"
        verbose_name_plural = "ventas"
        ordering = ["-fecha"]

    def calcular_totales(self, items=None):
        """Calcula subtotal, impuesto y total a partir de los ítems."""
        if items is None:
            items = self.items.all()
        self.subtotal = sum(
            (item.subtotal for item in items), Decimal("0.00")
        )
        self.impuesto = (self.subtotal * TASA_IVA).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.impuesto

    @property
    def tasa_iva_porcentaje(self):
        """Retorna la tasa de IVA como porcentaje entero (ej. 15)."""
        return int(TASA_IVA * 100)

    def __str__(self):
        return f"Venta {self.pk}"


class ItemVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="venta",
    )
    producto = models.ForeignKey(
        "usuarios.Producto",
        on_delete=models.PROTECT,
        related_name="items_venta",
        verbose_name="producto",
    )
    cantidad = models.PositiveIntegerField(verbose_name="cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="precio unitario"
    )

    class Meta:
        verbose_name = "ítem de venta"
        verbose_name_plural = "ítems de venta"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            self.producto.stock -= self.cantidad
            self.producto.save(update_fields=["stock"])

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
