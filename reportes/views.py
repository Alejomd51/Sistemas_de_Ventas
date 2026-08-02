from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

# Importa los modelos desde la app de ventas de Alejandro Molina
from ventas.models import Venta

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