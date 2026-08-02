from decimal import Decimal

from django.db import migrations


def crear_catalogo_inicial(apps, schema_editor):
    Categoria = apps.get_model("productos", "Categoria")
    Producto = apps.get_model("productos", "Producto")

    cafe, _ = Categoria.objects.get_or_create(
        nombre="Café",
        defaults={"descripcion": "Cafés y bebidas calientes", "activo": True},
    )
    cigarrillos, _ = Categoria.objects.get_or_create(
        nombre="Cigarrillos",
        defaults={
            "descripcion": "Productos de tabaco exclusivos para mayores de 18 años",
            "activo": True,
        },
    )

    productos = [
        ("Espresso", "Café intenso de extracción corta", Decimal("1.75"), 30, cafe),
        ("Cappuccino", "Espresso con leche vaporizada y espuma", Decimal("2.75"), 25, cafe),
        ("Americano", "Espresso suave alargado con agua caliente", Decimal("2.00"), 25, cafe),
        ("Cigarrillos clásicos", "Cajetilla de cigarrillos clásicos; venta +18", Decimal("6.00"), 20, cigarrillos),
        ("Cigarrillos mentolados", "Cajetilla mentolada; venta +18", Decimal("6.50"), 20, cigarrillos),
    ]
    for nombre, descripcion, precio, stock, categoria in productos:
        Producto.objects.get_or_create(
            nombre=nombre,
            categoria=categoria,
            defaults={
                "descripcion": descripcion,
                "precio": precio,
                "stock": stock,
                "activo": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("productos", "0001_initial")]

    operations = [migrations.RunPython(crear_catalogo_inicial, migrations.RunPython.noop)]
