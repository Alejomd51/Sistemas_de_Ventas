from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F
from django.db.models.signals import post_delete
from django.dispatch import receiver


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
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ventas",
        verbose_name="cliente",
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
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        with transaction.atomic():
            if self._state.adding:
                producto = ProductoParaStock.bloquear(self.producto_id)
                ProductoParaStock.validar_disponible(producto, self.cantidad)
                ProductoParaStock.ajustar(producto.pk, -self.cantidad)
            else:
                anterior = ItemVenta.objects.select_for_update().get(pk=self.pk)
                productos = ProductoParaStock.bloquear_varios(
                    anterior.producto_id,
                    self.producto_id,
                )

                if anterior.producto_id == self.producto_id:
                    diferencia = self.cantidad - anterior.cantidad
                    if diferencia > 0:
                        ProductoParaStock.validar_disponible(
                            productos[self.producto_id],
                            diferencia,
                        )
                    ProductoParaStock.ajustar(self.producto_id, -diferencia)
                else:
                    ProductoParaStock.validar_disponible(
                        productos[self.producto_id],
                        self.cantidad,
                    )
                    ProductoParaStock.ajustar(
                        anterior.producto_id,
                        anterior.cantidad,
                    )
                    ProductoParaStock.ajustar(self.producto_id, -self.cantidad)

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class ProductoParaStock:
    """Operaciones internas para actualizar inventario con bloqueo de filas."""

    @staticmethod
    def bloquear(producto_id):
        from usuarios.models import Producto

        return Producto.objects.select_for_update().get(pk=producto_id)

    @classmethod
    def bloquear_varios(cls, *producto_ids):
        from usuarios.models import Producto

        ids = sorted(set(producto_ids))
        return {
            producto.pk: producto
            for producto in Producto.objects.select_for_update().filter(pk__in=ids)
        }

    @staticmethod
    def validar_disponible(producto, cantidad):
        if producto.stock < cantidad:
            raise ValidationError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {producto.stock}."
            )

    @staticmethod
    def ajustar(producto_id, cantidad):
        from usuarios.models import Producto

        Producto.objects.filter(pk=producto_id).update(stock=F("stock") + cantidad)


@receiver(post_delete, sender=ItemVenta)
def restaurar_stock_al_eliminar_item(sender, instance, **kwargs):
    ProductoParaStock.ajustar(instance.producto_id, instance.cantidad)
