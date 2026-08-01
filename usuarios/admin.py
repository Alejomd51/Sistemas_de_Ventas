from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Categoria, Producto, Usuario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre", "descripcion")


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
