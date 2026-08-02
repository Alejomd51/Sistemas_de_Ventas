from django.contrib.auth.models import AbstractUser
from django.db import models


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
