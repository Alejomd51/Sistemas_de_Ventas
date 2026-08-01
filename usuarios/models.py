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

    @property
    def stock_bajo(self):
        return self.stock <= 5

    def __str__(self):
        return self.nombre



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
