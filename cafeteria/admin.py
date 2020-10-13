from django.contrib import admin
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from import_export.admin import ImportExportModelAdmin

from .models import DailyBalance
from .models import Expense
from .models import Income
from .models import Particular
from .models import Transaction


@admin.register(Particular)
class ParticularAdmin(ImportExportModelAdmin):
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
class IncomeAdmin(ImportExportModelAdmin):

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

    date_hierarchy = 'date'


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = [
        'date',
        'party',
        'amount',
        'is_expenditure',
        'remarks',
    ]

    def remarks(self, obj):
        return obj.reason

    list_filter = [
        'date',
        'party',
        'is_expenditure',
    ]

    date_hierarchy = 'date'


@admin.register(DailyBalance)
class DailyBalanceAdmin(ImportExportModelAdmin):

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


@receiver(post_save, sender=Income)
@receiver(post_save, sender=Expense)
@receiver(post_save, sender=Transaction)
def update_daily_balance_after_save(sender, instance, created, **kwargs):

    try:
        daily_balance = DailyBalance.objects.get(date=instance.date)
        daily_balance.save()
    except DailyBalance.DoesNotExist:
        # This will automatically call save() method.
        DailyBalance.objects.create(date=instance.date, opening_balance=0)


@receiver(post_delete, sender=Income)
@receiver(post_delete, sender=Expense)
@receiver(post_delete, sender=Transaction)
def update_daily_balance_after_delete(sender, instance, **kwargs):

    try:
        daily_balance = DailyBalance.objects.get(date=instance.date)
        if Income.objects.filter(date=instance.date).count() == 0 and Expense.objects.filter(date=instance.date).count() == 0 and Transaction.objects.filter(date=instance.date).count() == 0:
            daily_balance.delete()
        else:
            daily_balance.save()
    except DailyBalance.DoesNotExist:
        pass
