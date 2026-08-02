from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from productos.models import Producto

from .models import ItemVenta, Venta


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ("cliente", "metodo_pago")
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "metodo_pago": forms.Select(attrs={"class": "form-select"}),
        }


class ItemVentaForm(forms.ModelForm):
    """Formulario para cada ítem dentro de una venta."""

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True),
        widget=forms.Select(attrs={"class": "item-producto"}),
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "item-cantidad", "min": "1", "value": "1"}),
    )

    class Meta:
        model = ItemVenta
        fields = ("producto", "cantidad")


class ItemVentaBaseFormSet(BaseInlineFormSet):
    """Validación personalizada para el conjunto de ítems."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        productos_vistos = []
        tiene_items = False

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if not form.cleaned_data:
                continue

            tiene_items = True
            producto = form.cleaned_data.get("producto")
            cantidad = form.cleaned_data.get("cantidad")

            if producto in productos_vistos:
                raise forms.ValidationError(
                    f"El producto '{producto.nombre}' está duplicado. "
                    "Combine las cantidades en una sola línea."
                )
            productos_vistos.append(producto)

            if producto and cantidad and producto.stock < cantidad:
                form.add_error(
                    "cantidad",
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.stock}.",
                )

        if not tiene_items:
            raise forms.ValidationError("Debe agregar al menos un ítem a la venta.")


ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    formset=ItemVentaBaseFormSet,
    fields=("producto", "cantidad"),
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
