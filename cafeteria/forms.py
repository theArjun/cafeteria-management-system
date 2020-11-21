from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import (
    Income,
    Particular,
    Stock,
)


class IncomeAdminForm(forms.ModelForm):
    class Media:
        js = ('cafeteria/income/form_script.js', )

    class Meta:
        model = Income

        fields = [
            'date',
            'customer',
            'discount_percent',
            'discount_amount',
            'service_tax',
            'status',
            'remarks',
        ]

