from django.db import models

class Cliente(models.Model):
    TIPO_DOCUMENTO = [
        ('CEDULA', 'Cédula'),
        ('RUC', 'RUC'),
        ('PASAPORTE', 'Pasaporte'),
    ]

    identificacion = models.CharField(max_length=13, unique=True, verbose_name="Cédula / RUC")
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO, default='CEDULA')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.identificacion})"