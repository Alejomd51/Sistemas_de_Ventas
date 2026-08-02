from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'identificacion', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }