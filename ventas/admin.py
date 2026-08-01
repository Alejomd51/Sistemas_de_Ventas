from django.contrib import admin

from .models import ItemVenta, Venta


class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 1
    readonly_fields = ("subtotal",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("pk", "vendedor", "metodo_pago", "fecha", "subtotal", "impuesto", "total")
    list_filter = ("fecha", "metodo_pago")
    readonly_fields = ("subtotal", "impuesto", "total")
    inlines = [ItemVentaInline]


@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal")
