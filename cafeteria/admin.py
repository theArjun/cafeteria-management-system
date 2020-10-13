from django.contrib import admin

from .models import Expense
from .models import Income
from .models import Particular


@admin.register(Particular)
class ParticularAdmin(admin.ModelAdmin):
    list_display = [
        'particular',
        'cost_unit_price',
        'selling_unit_price',
        'bought_for',
    ]

    list_filter = [
        'particular',
        'bought_for',
    ]


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'customer',
        'particular',
        'quantity',
        'discount_percent',
        'status',
    ]

    list_display = [
        'customer',
        'date',
        'particular',
        'selling_unit_price',
        'quantity',
        'sub_total',
        'discount_percent',
        'net_total',
        'status',
    ]

    list_filter = [
        'customer',
        'date',
        'particular__particular',
        'status',
    ]

    def selling_unit_price(self, obj):
        return obj.particular.selling_unit_price


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'particular',
        'quantity',
        'bought_by',
        'bought_from',
        'status',
    ]

    list_display = [
        'date',
        'particular',
        'cost_unit_price',
        'quantity',
        'total_price',
        'bought_by',
        'bought_from',
        'status',
    ]

    list_filter = [
        'date',
        'particular__particular',
        'bought_by',
        'bought_from',
        'status'
    ]

    def cost_unit_price(self, obj):
        return obj.particular.cost_unit_price
