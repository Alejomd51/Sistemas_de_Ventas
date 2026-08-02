from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("identificacion", "nombres", "apellidos", "email", "telefono")
    list_filter = ("tipo_documento",)
    search_fields = ("identificacion", "nombres", "apellidos", "email")
