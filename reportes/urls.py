from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('ventas-periodo/', views.reporte_ventas_periodo, name='ventas_periodo'),
    path('top-productos/', views.dashboard_productos_mas_vendidos, name='top_productos'),
]