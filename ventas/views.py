from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import Usuario

from .forms import ItemVentaFormSet, VentaForm
from .models import Venta


@rol_requerido(Usuario.Rol.ADMIN, Usuario.Rol.VENDEDOR)
def ventas(request):
    ventas_list = (
        Venta.objects.select_related("vendedor")
        .prefetch_related("items__producto")
        .all()
    )
    if request.user.rol == Usuario.Rol.VENDEDOR:
        ventas_list = ventas_list.filter(vendedor=request.user)
    return render(request, "ventas/ventas.html", {"ventas": ventas_list})


@rol_requerido(Usuario.Rol.VENDEDOR)
def venta_crear(request):
    if request.method == "POST":
        venta = Venta(vendedor=request.user)
        venta_form = VentaForm(request.POST, instance=venta)
        formset = ItemVentaFormSet(request.POST, instance=venta)

        if venta_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = venta_form.save()
                items = formset.save(commit=False)
                for item in items:
                    item.precio_unitario = item.producto.precio
                    item.save()
                venta.calcular_totales(items)
                venta.save(update_fields=["subtotal", "impuesto", "total"])

            messages.success(request, "Venta registrada correctamente")
            return redirect("ventas:ventas")
    else:
        venta = Venta()
        venta_form = VentaForm(instance=venta)
        formset = ItemVentaFormSet(instance=venta)

    return render(request, "ventas/venta_form.html", {"formset": formset, "venta_form": venta_form})


@rol_requerido(Usuario.Rol.ADMIN, Usuario.Rol.VENDEDOR)
def venta_comprobante(request, pk):
    venta = get_object_or_404(Venta.objects.prefetch_related("items__producto"), pk=pk)
    
    if request.user.rol == Usuario.Rol.VENDEDOR and venta.vendedor != request.user:
        messages.error(request, "No tienes permiso para ver este comprobante.")
        return redirect("ventas:ventas")
        
    return render(request, "ventas/comprobante.html", {"venta": venta})
