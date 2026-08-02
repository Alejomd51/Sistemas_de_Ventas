from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("usuarios", "0005_producto_producto_stock_no_negativo"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Categoria",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("nombre", models.CharField(max_length=100, unique=True, verbose_name="nombre")),
                        ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
                        ("activo", models.BooleanField(default=True, verbose_name="activo")),
                    ],
                    options={
                        "db_table": "usuarios_categoria",
                        "verbose_name": "categoría",
                        "verbose_name_plural": "categorías",
                        "ordering": ["nombre"],
                    },
                ),
                migrations.CreateModel(
                    name="Producto",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("nombre", models.CharField(max_length=150, verbose_name="nombre")),
                        ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
                        ("precio", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="precio")),
                        ("stock", models.IntegerField(default=0, verbose_name="stock")),
                        ("activo", models.BooleanField(default=True, verbose_name="activo")),
                        (
                            "categoria",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="productos",
                                to="productos.categoria",
                                verbose_name="categoría",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "usuarios_producto",
                        "verbose_name": "producto",
                        "verbose_name_plural": "productos",
                        "ordering": ["nombre"],
                        "constraints": [
                            models.CheckConstraint(
                                condition=models.Q(("stock__gte", 0)),
                                name="producto_stock_no_negativo",
                            )
                        ],
                    },
                ),
            ],
        ),
    ]
