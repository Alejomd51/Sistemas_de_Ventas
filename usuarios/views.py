from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm, RegistroUsuarioForm, VentaForm
from .decorators import rol_requerido
from .models import DetalleVenta, Producto, Usuario, Venta


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
@rol_requerido(Usuario.Rol.VENDEDOR)
def ventas(request):
    ventas_list = Venta.objects.prefetch_related("detalles").all()
    return render(request, "usuarios/ventas.html", {"ventas": ventas_list})


@login_required
@rol_requerido(Usuario.Rol.VENDEDOR)
def venta_crear(request):
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data["producto"]
            cantidad = form.cleaned_data["cantidad"]
            if producto.stock < cantidad:
                messages.error(request, "No hay suficiente stock para esta venta.")
            else:
                venta = Venta.objects.create()
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )
                venta.total = sum(detalle.subtotal for detalle in venta.detalles.all())
                venta.save(update_fields=["total"])
                messages.success(request, "Venta registrada correctamente")
                return redirect("usuarios:ventas")
    else:
        form = VentaForm()

    return render(request, "usuarios/venta_form.html", {"form": form})


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

    return render(request, "usuarios/producto_form.html", {"form": form, "accion": "Crear"})


@login_required
@rol_requerido(Usuario.Rol.ADMIN)
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("usuarios:productos")
    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        "usuarios/producto_form.html",
        {"form": form, "accion": "Editar", "producto": producto},
    )


@login_required
@rol_requerido(Usuario.Rol.ADMIN)
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto eliminado correctamente: {nombre}")
        return redirect("usuarios:productos")

    return render(request, "usuarios/producto_confirm_delete.html", {"producto": producto})


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
