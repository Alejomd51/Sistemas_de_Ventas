from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('ventas-periodo/', views.reporte_ventas_periodo, name='ventas_periodo'),
]