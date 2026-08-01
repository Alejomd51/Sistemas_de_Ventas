from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistroUsuarioForm
from .decorators import rol_requerido
from .models import Usuario


@login_required
def inicio(request):
    return render(request, "usuarios/inicio.html")


@rol_requerido(Usuario.Rol.ADMIN)
def panel_admin(request):
    return render(request, "usuarios/panel_admin.html")


@rol_requerido(Usuario.Rol.VENDEDOR)
def panel_vendedor(request):
    return render(request, "usuarios/panel_vendedor.html")


def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("usuarios:registro")
    else:
        form = RegistroUsuarioForm()

    return render(request, "usuarios/registro.html", {"form": form})
