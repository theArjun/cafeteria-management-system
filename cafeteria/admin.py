from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from import_export.admin import ImportExportModelAdmin

from .forms import IncomeAdminForm
from .models import CafeteriaManager
from .models import Credit
from .models import DailyBalance
from .models import Expense
from .models import Incentive
from .models import Income
from .models import Particular
from .models import Penalty
from .models import Stock
from .models import Transaction


@admin.register(CafeteriaManager)
class CafeteriaManagerAdmin(ImportExportModelAdmin):

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


@admin.register(Incentive)
class IncentiveAdmin(ImportExportModelAdmin):

    list_display = [
        'date',
        'manager',
        'amount',
    ]

    list_filter = [
        'date',
        'manager__name',
    ]

    date_hierarchy = 'date'

class ExpenseInline(admin.TabularInline):
    model = Expense
    exclude = ['remarks', 'total_price']


@admin.register(Particular)
class ParticularAdmin(ImportExportModelAdmin):

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


@admin.register(Income)
class IncomeAdmin(ImportExportModelAdmin):

    form = IncomeAdminForm

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

    date_hierarchy = 'date'

    def selling_unit_price(self, obj):
        return obj.particular.selling_unit_price

    date_hierarchy = 'date'


@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin):

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
class TransactionAdmin(ImportExportModelAdmin):

    fields = [
        'date',
        'party',
        'amount',
        'is_expenditure',
        'remarks',
    ]

    list_display = [
        'date',
        'party',
        'amount',
        'is_expenditure',
    ]

    list_filter = [
        'date',
        'party',
        'is_expenditure',
    ]

    date_hierarchy = 'date'


@admin.register(DailyBalance)
class DailyBalanceAdmin(ImportExportModelAdmin):

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
        'incoming_balance',
        'outgoing_balance',
        'closing_balance',
    ]

    list_filter = [
        'date',
    ]

    date_hierarchy = 'date'

    def income(self, obj):
        return Income.objects.filter(date=obj.date).aggregate(
            total=Sum('net_total')).get('total', 0.0)

    def expense(self, obj):
        return Expense.objects.filter(date=obj.date).aggregate(
            total=Sum('total_price')).get('total', 0.0)

    def incoming_balance(self, obj):
        return Transaction.objects.filter(
            date=obj.date, is_expenditure=False).aggregate(total=Sum('amount')).get('total', 0.0)

    def outgoing_balance(self, obj):
        return Transaction.objects.filter(
            date=obj.date, is_expenditure=True).aggregate(total=Sum('amount')).get('total', 0.0)


@admin.register(Stock)
class StockAdmin(ImportExportModelAdmin):

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


@admin.register(Credit)
class CreditAdmin(ImportExportModelAdmin):

    list_display = [
        'transaction',
        'date',
        'net_total',
        'mark_as_cleared',
    ]

    list_filter = [
        'transaction__customer',
        'mark_as_cleared',
        'date'
    ]

    date_hierarchy = 'date'

    def has_add_permission(self, request):
        return False

    def date(self, obj):
        return obj.transaction.date

    def net_total(self, obj):
        return obj.transaction.net_total


@admin.register(Penalty)
class PenaltyAdmin(ImportExportModelAdmin):

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


