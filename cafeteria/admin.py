from django.contrib import admin
from django.db.models import Sum
from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver
from django.utils.html import mark_safe

from .forms import IncomeAdminForm
# from .models import Incentive
from .models import (
    CafeteriaManager,
    Customer,
    DailyBalance,
    Expense,
    Income,
    Particular,
    Penalty,
    SaleItem,
    Stock,
    Transaction,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    '''Admin View for Customer'''

    fields = [
        'name',
        'phone_number',
        'reserve_balance',
        'credit_balance',
        'remarks',
    ]

    list_display = [
        'name',
        'phone_number',
        'reserve_balance',
        'credit_balance',
        'remarks'
    ]


@admin.register(CafeteriaManager)
class CafeteriaManagerAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'phone_number',
        'address',
        'joined_date',
        'is_active',
    ]

    list_filter = [
        'name',
        'address',
        'is_active',
    ]

class ExpenseInline(admin.TabularInline):
    model = Expense
    exclude = ['remarks', 'total_price']


@admin.register(Particular)
class ParticularAdmin(admin.ModelAdmin):

    fields = [
        'particular',
        'cost_unit_price',
        'selling_unit_price',
        'bought_for',
        'remarks',
    ]

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

    inlines = [ExpenseInline, ]



class SaleItemInline(admin.TabularInline):
    '''Tabular Inline View for SaleItem'''

    model = SaleItem
    exclude = ['total', ]



@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):

    form = IncomeAdminForm
    inlines = [SaleItemInline]

    fieldsets = (
        (None, {
            'fields': (
                'date',
                'customer',
                # 'is_sold_after_6_pm',
                'status'
            )
        }),
        ('Remarks', {
            'classes': ('collapse',),
            'fields': ('remarks',),
        }),
        ('Extra', {
            'classes': ('collapse',),
            'fields': (
                'discount_percent',
                'discount_amount',
                'service_tax'
            ),
        }),
    )

    list_display = [
        'customer',
        'date',
        'particulars',
        'sub_total',
        'discount_percent',
        'discount_amount',
        'service_tax',
        'net_total',
        'status',
    ]

    list_filter = [
        'customer',
        'date',
        'status',
    ]

    date_hierarchy = 'date'
    empty_value_display = 'N/A'

    def sub_total(self, obj):
        total = 0.0
        for sale in obj.sales.all():
            price = sale.particular.selling_unit_price * sale.quantity
            total += price
        return total

    def net_total(self, obj):
        service_tax = obj.service_tax
        service_tax_added_price = self.sub_total(
            obj) * (100 + service_tax) / 100
        discount_percent = obj.discount_percent
        after_discount_price = service_tax_added_price * \
            (100 - discount_percent) / 100
        after_discount_price = after_discount_price - obj.discount_amount
        return after_discount_price

    def particulars(self, obj):
        items = []

        for sale in obj.sales.all():
            items.append(
                (
                    f'{sale.particular}',  sale.quantity
                )
            )
            dropdown_html = []
            for item in items:
                d_item = f'<a class="dropdown-item" href="#">{item[0]} | {item[1]}</a>'
                dropdown_html.append(d_item)

            html = """
                <div class="dropdown">
                <button class="btn btn-light dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Click to view
                </button>
                <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                    {}
                </div>
                </div>
        """.format(''.join(dropdown_html))
        return mark_safe(html)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'particular',
        'quantity',
        'bought_by',
        'bought_from',
        'status',
        'remarks',
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

    date_hierarchy = 'date'

    def cost_unit_price(self, obj):
        return obj.particular.cost_unit_price

    date_hierarchy = 'date'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'party',
        'amount',
        'is_outgoing',
        'remarks',
    ]

    list_display = [
        'date',
        'party',
        'amount',
        'is_outgoing',
    ]

    list_filter = [
        'date',
        'party',
        'is_outgoing',
    ]

    date_hierarchy = 'date'


@admin.register(DailyBalance)
class DailyBalanceAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'opening_balance',
        'remarks',
    ]

    list_display = [
        'date',
        'opening_balance',
        'income',
        'expense',
        'penalty',
        'incoming_balance',
        'outgoing_balance',
        'closing_balance',
    ]

    list_filter = [
        'date',
    ]

    date_hierarchy = 'date'

    def income(self, obj):
        total = 0
        incomes = Income.objects.filter(date=obj.date)
        for income in incomes:
            sale_items = income.sales.all()
            for sale in sale_items:
                total += (sale.particular.selling_unit_price * sale.quantity)

        return total

    def penalty(self, obj):
        total = 0
        penalties = Penalty.objects.filter(date=obj.date)
        for penalty in penalties:
            total += penalty.charge

        return total


    def expense(self, obj):
        return Expense.objects.filter(date=obj.date).aggregate(
            total=Sum('total_price')).get('total', 0.0)

    def incoming_balance(self, obj):
        return Transaction.objects.filter(
            date=obj.date, is_outgoing=False).aggregate(total=Sum('amount')).get('total', 0.0)

    def outgoing_balance(self, obj):
        return Transaction.objects.filter(
            date=obj.date, is_outgoing=True).aggregate(total=Sum('amount')).get('total', 0.0)

    def closing_balance(self, obj):
        return (obj.opening_balance + self.income(obj) - self.expense(obj) \
            + self.incoming_balance(obj) - self.outgoing_balance(obj) \
            + self.penalty(obj)
)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    fields = [
        'particular',
        'item_remaining',
    ]

    list_display = [
        'particular',
        'item_remaining',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):

    fields = [
        'date',
        'party',
        'charge',
        'is_fulfilled',
        'remarks',
    ]

    list_display = [
        'party',
        'date',
        'charge',
        'is_fulfilled',
        'remarks',
    ]

    list_filter = [
        'party',
        'date',
        'is_fulfilled',
    ]

    date_hierarchy = 'date'


