from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("productos", "0001_initial"),
        ("ventas", "0004_venta_cliente"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="itemventa",
                    name="producto",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="items_venta",
                        to="productos.producto",
                        verbose_name="producto",
                    ),
                ),
            ],
        ),
    ]
