from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.productos, name="productos"),
    path("crear/", views.producto_crear, name="producto_crear"),
    path("<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("<int:pk>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
]
