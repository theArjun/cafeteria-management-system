from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Income
from .models import Particular
from .models import Stock


class IncomeAdminForm(forms.ModelForm):

    class Meta:
        model = Income

        fields = [
            'date',
            'customer',
            'particular',
            'quantity',
            'discount_percent',
            'service_tax',
            'is_sold_after_6_pm',
            'status',
            'remarks',
        ]

    def clean(self):
        cleaned_data = self.cleaned_data
        particular = cleaned_data.get('particular')
        quantity = cleaned_data.get('quantity')
        try:
            particular_stock = Stock.objects.get(particular=particular)
            if particular_stock.item_remaining < quantity:
                raise forms.ValidationError(
                    _(f'You requested {quantity} no. of item for {particular}. {particular} has {particular_stock.item_remaining} in stock.')
                )
        except Stock.DoesNotExist:
            raise forms.ValidationError(
                _(f'{particular} has no data in stock. Please update the stock first.')
            )
        return cleaned_data
