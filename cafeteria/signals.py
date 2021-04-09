from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver

from .models import (
    DailyBalance,
    Expense,
    Income,
    SaleItem,
    Stock,
    Transaction,
)


@receiver(post_save, sender=Income)
@receiver(post_save, sender=Expense)
@receiver(post_save, sender=Transaction)
def update_daily_balance_after_save(sender, instance, created, **kwargs):
    """Updates daily function after models : Income, Expense and Transaction
        are updated.

    Args:
        sender (Model): The model which invoke this function.
        instance (Model Instance): The instance of the model
        which invoke this function.
        created (Boolean): If the instance is newly created,
        it returns true; if modified / not newly created return false.
    """
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
        if (
            not Income.objects.filter(date=instance.date).exists()
            and not Expense.objects.filter(date=instance.date).exists()
            and not Transaction.objects.filter(date=instance.date).exists()
        ):
            daily_balance.delete()
        else:
            daily_balance.save()
    except DailyBalance.DoesNotExist:
        pass


@receiver(post_save, sender=SaleItem)
def update_stock_after_sales(sender, instance, created, **kwargs):
    sale_item = instance
    particular = sale_item.particular
    if particular.bought_for == 'BOTH':
        try:
            stock = Stock.objects.get(particular=particular)
            stock.item_remaining -= sale_item.quantity
            stock.save()
        except Stock.DoesNotExist:
            pass
    else:
        pass


@receiver(post_save, sender=Income)
def add_credit_to_customer_account(sender, instance, created, **kwargs):
    income_instance = instance
    if income_instance.status == Income.Types.CREDIT or income_instance.status == Income.Types.RESERVE:
        bill = 0
        sale_items = income_instance.sales.all()
        for sale in sale_items:
            bill += (sale.particular.selling_unit_price * sale.quantity)
        customer = income_instance.customer
        customer.credit_balance += bill
        print('hello')
        customer.save()
    else:
        pass
