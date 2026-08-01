from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Producto, Usuario


class VentaForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(activo=True))
    cantidad = forms.IntegerField(min_value=1)


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "precio", "stock", "categoria", "activo")


class RegistroUsuarioForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "first_name", "last_name", "email", "rol")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email
