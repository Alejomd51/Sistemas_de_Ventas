from decimal import Decimal

from django.db import migrations


CATALOGO = [
    ("Latte", "Espresso con abundante leche vaporizada", Decimal("3.00"), 25, "Café"),
    ("Mocaccino", "Café con leche, chocolate y espuma", Decimal("3.50"), 20, "Café"),
    ("Macchiato", "Espresso marcado con una pequeña capa de leche", Decimal("2.25"), 20, "Café"),
    ("Cortado", "Espresso equilibrado con leche caliente", Decimal("2.50"), 20, "Café"),
    ("Cold brew", "Café extraído en frío, suave y refrescante", Decimal("3.75"), 18, "Café"),
    ("Café filtrado", "Café de especialidad preparado por filtrado", Decimal("2.50"), 25, "Café"),
    ("Cigarrillo clásico - unidad", "Cigarrillo clásico individual; venta exclusiva +18", Decimal("0.50"), 100, "Cigarrillos"),
    ("Cigarrillo mentolado - unidad", "Cigarrillo mentolado individual; venta exclusiva +18", Decimal("0.60"), 100, "Cigarrillos"),
    ("Cigarrillo premium - unidad", "Cigarrillo premium individual; venta exclusiva +18", Decimal("0.75"), 80, "Cigarrillos"),
]


def agregar_productos(apps, schema_editor):
    Categoria = apps.get_model("productos", "Categoria")
    Producto = apps.get_model("productos", "Producto")
    categorias = {categoria.nombre: categoria for categoria in Categoria.objects.all()}

    for nombre, descripcion, precio, stock, categoria_nombre in CATALOGO:
        Producto.objects.get_or_create(
            nombre=nombre,
            categoria=categorias[categoria_nombre],
            defaults={
                "descripcion": descripcion,
                "precio": precio,
                "stock": stock,
                "activo": True,
            },
        )


def quitar_productos(apps, schema_editor):
    Producto = apps.get_model("productos", "Producto")
    Producto.objects.filter(nombre__in=[fila[0] for fila in CATALOGO]).delete()


class Migration(migrations.Migration):
    dependencies = [("productos", "0002_catalogo_inicial_cafeteria")]
    operations = [migrations.RunPython(agregar_productos, quitar_productos)]
