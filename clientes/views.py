from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from usuarios.decorators import rol_requerido
from usuarios.models import Usuario
from .models import Cliente
from .forms import ClienteForm


@rol_requerido(Usuario.Rol.ADMIN, Usuario.Rol.VENDEDOR)
def lista_clientes(request):
    query = request.GET.get('q', '')
    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(
            Q(identificacion__icontains=query) |
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query)
        )

    return render(request, 'clientes/lista.html', {'clientes': clientes, 'query': query})

@rol_requerido(Usuario.Rol.ADMIN, Usuario.Rol.VENDEDOR)
def registro_rapido_cliente(request):
    """Vista pensada para registrar un cliente rápido desde la interfaz de venta o modal."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'cliente_id': cliente.id,
                    'nombre_completo': f"{cliente.nombres} {cliente.apellidos}"
                })
            return redirect('clientes:lista')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/form_modal.html', {'form': form})

@rol_requerido(Usuario.Rol.ADMIN, Usuario.Rol.VENDEDOR)
def historial_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    ventas = cliente.ventas.select_related("vendedor").prefetch_related("items__producto")
    
    # Cálculo de métricas del cliente
    total_gastado = sum(v.total for v in ventas) if ventas else 0
    total_compras = ventas.count()

    context = {
        'cliente': cliente,
        'ventas': ventas,
        'total_gastado': total_gastado,
        'total_compras': total_compras,
    }
    return render(request, 'clientes/historial.html', context)
