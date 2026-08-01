from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProductoForm, RegistroUsuarioForm
from .decorators import rol_requerido
from .models import Producto, Usuario


@login_required
def inicio(request):
    return render(request, "usuarios/inicio.html")


@rol_requerido(Usuario.Rol.ADMIN)
def panel_admin(request):
    return render(request, "usuarios/panel_admin.html")


@rol_requerido(Usuario.Rol.VENDEDOR)
def panel_vendedor(request):
    return render(request, "usuarios/panel_vendedor.html")


@login_required
@rol_requerido(Usuario.Rol.ADMIN)
def productos(request):
    productos_list = Producto.objects.select_related("categoria").all()
    return render(request, "usuarios/productos.html", {"productos": productos_list})


@login_required
@rol_requerido(Usuario.Rol.ADMIN)
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(
                request,
                f"Producto '{producto.nombre}' creado correctamente.",
            )
            return redirect("usuarios:productos")
    else:
        form = ProductoForm()

    return render(request, "usuarios/producto_form.html", {"form": form})


def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Usuario registrado correctamente. Ya puedes iniciar sesión.",
            )
            return redirect("usuarios:login")
    else:
        form = RegistroUsuarioForm()

    return render(request, "usuarios/registro.html", {"form": form})
