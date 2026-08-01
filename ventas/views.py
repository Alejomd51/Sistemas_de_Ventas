from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import Usuario

from .forms import ItemVentaFormSet
from .models import Venta


@login_required
@rol_requerido(Usuario.Rol.VENDEDOR)
def ventas(request):
    ventas_list = (
        Venta.objects.select_related("vendedor")
        .prefetch_related("items__producto")
        .all()
    )
    return render(request, "ventas/ventas.html", {"ventas": ventas_list})


@login_required
@rol_requerido(Usuario.Rol.VENDEDOR)
def venta_crear(request):
    if request.method == "POST":
        venta = Venta(vendedor=request.user)
        formset = ItemVentaFormSet(request.POST, instance=venta)

        if formset.is_valid():
            with transaction.atomic():
                venta.save()
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
        formset = ItemVentaFormSet(instance=venta)

    return render(request, "ventas/venta_form.html", {"formset": formset})
