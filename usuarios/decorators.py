from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def rol_requerido(*roles_permitidos):
    """Permite acceder únicamente a usuarios con uno de los roles indicados."""

    def decorador(view_func):
        @login_required
        @wraps(view_func)
        def vista_protegida(request, *args, **kwargs):
            if request.user.rol not in roles_permitidos:
                raise PermissionDenied("No tienes permisos para acceder a esta página.")
            return view_func(request, *args, **kwargs)

        return vista_protegida

    return decorador
