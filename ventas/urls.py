from django.urls import path

from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.ventas, name="ventas"),
    path("crear/", views.venta_crear, name="venta_crear"),
]
