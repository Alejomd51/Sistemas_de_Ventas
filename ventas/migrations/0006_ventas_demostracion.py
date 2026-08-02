from decimal import Decimal

from django.db import migrations


VENTAS = [
    ("1700000001", "EFECTIVO", [("Cappuccino", 2), ("Cigarrillo clásico - unidad", 3)]),
    ("1700000002", "TARJETA", [("Cold brew", 1), ("Cigarrillo mentolado - unidad", 2)]),
    ("1790000001001", "TRANSFERENCIA", [("Latte", 2), ("Mocaccino", 1)]),
    ("PA000004", "EFECTIVO", [("Espresso", 1), ("Cigarrillo premium - unidad", 4)]),
    ("1700000005", "TARJETA", [("Café filtrado", 2), ("Cortado", 1)]),
]


def crear_ventas(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    Producto = apps.get_model("productos", "Producto")
    Venta = apps.get_model("ventas", "Venta")
    ItemVenta = apps.get_model("ventas", "ItemVenta")

    for identificacion, metodo_pago, items in VENTAS:
        cliente = Cliente.objects.get(identificacion=identificacion)
        if Venta.objects.filter(cliente=cliente, vendedor__isnull=True).exists():
            continue

        venta = Venta.objects.create(cliente=cliente, metodo_pago=metodo_pago)
        subtotal = Decimal("0.00")
        for nombre_producto, cantidad in items:
            producto = Producto.objects.get(nombre=nombre_producto)
            ItemVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )
            producto.stock -= cantidad
            producto.save(update_fields=["stock"])
            subtotal += producto.precio * cantidad

        impuesto = (subtotal * Decimal("0.15")).quantize(Decimal("0.01"))
        venta.subtotal = subtotal
        venta.impuesto = impuesto
        venta.total = subtotal + impuesto
        venta.save(update_fields=["subtotal", "impuesto", "total"])


def quitar_ventas(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    Producto = apps.get_model("productos", "Producto")
    Venta = apps.get_model("ventas", "Venta")

    ventas = Venta.objects.filter(
        cliente__identificacion__in=[fila[0] for fila in VENTAS],
        vendedor__isnull=True,
    ).prefetch_related("items")
    for venta in ventas:
        for item in venta.items.all():
            producto = Producto.objects.get(pk=item.producto_id)
            producto.stock += item.cantidad
            producto.save(update_fields=["stock"])
        venta.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0002_clientes_demostracion"),
        ("productos", "0003_ampliar_catalogo_cafeteria"),
        ("ventas", "0005_mover_producto_a_productos"),
    ]
    operations = [migrations.RunPython(crear_ventas, quitar_ventas)]
