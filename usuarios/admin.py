from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Categoria, DetalleVenta, Producto, Usuario, Venta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre", "descripcion")


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("pk", "fecha", "total")


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Sistema de ventas", {"fields": ("rol",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Sistema de ventas", {"fields": ("rol",)}),
    )
    list_display = ("username", "email", "first_name", "last_name", "rol", "is_staff")
    list_filter = UserAdmin.list_filter + ("rol",)
