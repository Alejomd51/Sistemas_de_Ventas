from django.db import migrations


CLIENTES = [
    ("1700000001", "CEDULA", "Sofía", "Vega", "sofia.vega@example.com", "0991000001", "Quito"),
    ("1700000002", "CEDULA", "Mateo", "Paredes", "mateo.paredes@example.com", "0991000002", "Cumbayá"),
    ("1790000001001", "RUC", "Valentina", "Ruiz", "valentina.ruiz@example.com", "0991000003", "Tumbaco"),
    ("PA000004", "PASAPORTE", "Daniel", "Silva", "daniel.silva@example.com", "0991000004", "Quito"),
    ("1700000005", "CEDULA", "Camila", "Torres", "camila.torres@example.com", "0991000005", "Valle de los Chillos"),
]


def crear_clientes(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    for identificacion, tipo, nombres, apellidos, email, telefono, direccion in CLIENTES:
        Cliente.objects.get_or_create(
            identificacion=identificacion,
            defaults={
                "tipo_documento": tipo,
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email,
                "telefono": telefono,
                "direccion": direccion,
            },
        )


def quitar_clientes(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    Cliente.objects.filter(identificacion__in=[fila[0] for fila in CLIENTES]).delete()


class Migration(migrations.Migration):
    dependencies = [("clientes", "0001_initial")]
    operations = [migrations.RunPython(crear_clientes, quitar_clientes)]
