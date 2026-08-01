from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("panel-admin/", views.panel_admin, name="panel_admin"),
    path("panel-vendedor/", views.panel_vendedor, name="panel_vendedor"),
    path("ventas/", views.ventas, name="ventas"),
    path("ventas/crear/", views.venta_crear, name="venta_crear"),
    path("productos/", views.productos, name="productos"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("productos/<int:pk>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="usuarios/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "recuperar-contrasena/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/password_reset_form.html",
            email_template_name="usuarios/password_reset_email.html",
            subject_template_name="usuarios/password_reset_subject.txt",
            success_url="/usuarios/recuperar-contrasena/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "recuperar-contrasena/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "restablecer/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/password_reset_confirm.html",
            success_url="/usuarios/restablecer/completado/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "restablecer/completado/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
