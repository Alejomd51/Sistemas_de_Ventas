from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

# Importamos los modelos de la app de ventas
# (Asegúrate de importar ItemVenta para el Paso 5)
from ventas.models import Venta, ItemVenta

def reporte_ventas_periodo(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Rango por defecto: últimos 30 días
    hoy = datetime.now().date()
    fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else hoy - timedelta(days=30)
    fecha_fin = parse_date(fecha_fin_str) if fecha_fin_str else hoy

    ventas = Venta.objects.filter(fecha_venta__date__range=[fecha_inicio, fecha_fin])

    # Agregación por día usando Django ORM
    ventas_por_dia = (
        ventas.annotate(dia=TruncDay('fecha_venta'))
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

def dashboard_productos_mas_vendidos(request):
    # Top 10 productos más vendidos
    top_productos = (
        ItemVenta.objects.values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'), ingresos=Sum('subtotal'))
        .order_by('-total_vendido')[:10]
    )

    labels = [p['producto__nombre'] for p in top_productos]
    data_cantidades = [p['total_vendido'] for p in top_productos]
    data_ingresos = [float(p['ingresos']) for p in top_productos]

    context = {
        'top_productos': top_productos,
        'chart_labels': labels,
        'chart_cantidades': data_cantidades,
        'chart_ingresos': data_ingresos,
    }
    return render(request, 'reportes/top_productos.html', context)