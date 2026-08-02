from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("productos", "0001_initial"),
        ("usuarios", "0005_producto_producto_stock_no_negativo"),
        ("ventas", "0005_mover_producto_a_productos"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="Producto"),
                migrations.DeleteModel(name="Categoria"),
            ],
        ),
    ]
