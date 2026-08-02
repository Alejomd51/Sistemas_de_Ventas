from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista'),
    path('registro-rapido/', views.registro_rapido_cliente, name='registro_rapido'),
]