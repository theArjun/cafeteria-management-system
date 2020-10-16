from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Credit
from .models import DailyBalance
from .models import Expense
from .models import Income
from .models import Transaction


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


@receiver(post_save, sender=Income)
def update_credit_from_sale(sender, instance, created, **kwargs):
    if instance.status == instance.Types.CREDIT:
        credit = Credit.objects.create(
            date=instance.date,
            transaction=instance,
        )
