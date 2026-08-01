from django.contrib.auth.models import AbstractUser
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="nombre")
    descripcion = models.TextField(blank=True, verbose_name="descripción")
    activo = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="nombre")
    descripcion = models.TextField(blank=True, verbose_name="descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio")
    stock = models.IntegerField(default=0, verbose_name="stock")
    activo = models.BooleanField(default=True, verbose_name="activo")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="categoría",
    )

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["nombre"]

    @property
    def precio_formateado(self):
        return f"{self.precio:.2f}"

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="fecha")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="total")

    class Meta:
        verbose_name = "venta"
        verbose_name_plural = "ventas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta {self.pk}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        related_name="detalles",
        on_delete=models.CASCADE,
        verbose_name="venta",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles",
        verbose_name="producto",
    )
    cantidad = models.PositiveIntegerField(verbose_name="cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio unitario")

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"

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


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        VENDEDOR = "VENDEDOR", "Vendedor"

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.VENDEDOR,
        verbose_name="rol",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.username
