from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import Usuario

from .forms import ProductoForm
from .models import Producto


@rol_requerido(Usuario.Rol.ADMIN)
def productos(request):
    productos_list = Producto.objects.select_related("categoria").all()
    return render(request, "productos/productos.html", {"productos": productos_list})


@rol_requerido(Usuario.Rol.ADMIN)
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto '{producto.nombre}' creado correctamente.")
            return redirect("productos:productos")
    else:
        form = ProductoForm()
    return render(request, "productos/producto_form.html", {"form": form, "accion": "Crear"})


@rol_requerido(Usuario.Rol.ADMIN)
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos:productos")
    else:
        form = ProductoForm(instance=producto)
    return render(
        request,
        "productos/producto_form.html",
        {"form": form, "accion": "Editar", "producto": producto},
    )


@rol_requerido(Usuario.Rol.ADMIN)
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto eliminado correctamente: {nombre}")
        return redirect("productos:productos")
    return render(request, "productos/producto_confirm_delete.html", {"producto": producto})
