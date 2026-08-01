from django import forms

from usuarios.models import Producto


class VentaForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(activo=True))
    cantidad = forms.IntegerField(min_value=1)
