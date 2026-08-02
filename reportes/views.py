from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import timedelta

from usuarios.decorators import rol_requerido
from usuarios.models import Usuario
from ventas.models import Venta, ItemVenta


@rol_requerido(Usuario.Rol.ADMIN)
def reporte_ventas_periodo(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Rango por defecto: últimos 30 días
    hoy = timezone.localdate()
    fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else hoy - timedelta(days=30)
    fecha_fin = parse_date(fecha_fin_str) if fecha_fin_str else hoy

    ventas = Venta.objects.filter(fecha__date__range=[fecha_inicio, fecha_fin])

    # Agregación por día usando Django ORM
    ventas_por_dia = (
        ventas.annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(total_ventas=Sum('total'), cantidad_ordenes=Count('id'))
        .order_by('dia')
    )

    monto_total_periodo = ventas.aggregate(total=Sum('total'))['total'] or 0
    total_transacciones = ventas.count()

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ventas_por_dia': ventas_por_dia,
        'monto_total_periodo': monto_total_periodo,
        'total_transacciones': total_transacciones,
    }
    return render(request, 'reportes/ventas_periodo.html', context)


@rol_requerido(Usuario.Rol.ADMIN)
def dashboard_productos_mas_vendidos(request):
    # Top 10 productos más vendidos
    top_productos = (
        ItemVenta.objects.values('producto__nombre')
        .annotate(
            total_vendido=Sum('cantidad'),
            ingresos=Sum(
                F('cantidad') * F('precio_unitario'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .order_by('-total_vendido')[:10]
    )

    top_productos = list(top_productos)
    max_vendido = max((p['total_vendido'] for p in top_productos), default=0)
    for producto in top_productos:
        producto['porcentaje'] = (
            round(producto['total_vendido'] * 100 / max_vendido) if max_vendido else 0
        )

    context = {
        'top_productos': top_productos,
    }
    return render(request, 'reportes/top_productos.html', context)
