from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Usuario


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
