from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import Usuario

from .forms import VentaForm
from .models import ItemVenta, Venta


@login_required
@rol_requerido(Usuario.Rol.VENDEDOR)
def ventas(request):
    ventas_list = Venta.objects.select_related("vendedor").prefetch_related("items").all()
    return render(request, "ventas/ventas.html", {"ventas": ventas_list})


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
                venta = Venta.objects.create(vendedor=request.user)
                ItemVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )
                venta.total = sum(item.subtotal for item in venta.items.all())
                venta.save(update_fields=["total"])
                messages.success(request, "Venta registrada correctamente")
                return redirect("ventas:ventas")
    else:
        form = VentaForm()

    return render(request, "ventas/venta_form.html", {"form": form})
