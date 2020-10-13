from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from utils.fields import PercentField
from utils.functions import calculate_percentage
from utils.models import TimeStampedModelMixin


class Particular(TimeStampedModelMixin):

    class Purpose(models.TextChoices):
        INPUT = "INPUT", "Input"
        OUTPUT = "OUTPUT", "Output"
        BOTH = "BOTH", "Both"

    particular = models.CharField(max_length=255)
    cost_unit_price = models.FloatField()
    selling_unit_price = models.FloatField()
    bought_for = models.CharField(
        _("Purpose"),
        max_length=50,
        choices=Purpose.choices,
        default=Purpose.OUTPUT
    )

    def __str__(self):
        return f'{self.particular}'


class Income(TimeStampedModelMixin):

    class Types(models.TextChoices):
        CASH = "CASH", "Cash"
        CREDIT = "CREDIT", "Credit"

    date = models.DateField()
    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    sub_total = models.FloatField()
    discount_percent = PercentField(_('Discount Percent'))
    net_total = models.FloatField()
    customer = models.CharField(max_length=255)
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=Types.choices,
        default=Types.CASH
    )

    def __str__(self):
        return f'{self.customer}'

    def save(self, *args, **kwargs):

        selling_unit_price = self.particular.selling_unit_price
        self.sub_total = self.quantity * selling_unit_price
        self.net_total = calculate_percentage(
            amount=self.sub_total,
            percent=self.discount_percent,
            method='-'
        )

        super(Income, self).save(*args, **kwargs)


class Expense(TimeStampedModelMixin):

    class Types(models.TextChoices):
        CASH = "CASH", "Cash"
        CREDIT = "CREDIT", "Credit"

    date = models.DateField()
    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    total_price = models.FloatField()
    bought_by = models.CharField(max_length=255)
    bought_from = models.CharField(max_length=255)
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=Types.choices,
        default=Types.CASH
    )

    def __str__(self):
        return f'{self.particular}'

    def save(self, *args, **kwargs):

        cost_unit_price = self.particular.cost_unit_price
        self.total_price = self.quantity * cost_unit_price

        super(Expense, self).save(*args, **kwargs)


class Transaction(TimeStampedModelMixin):

    date = models.DateField()
    party = models.CharField(max_length=255)
    reason = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField()
    is_expenditure = models.BooleanField(
        _('Is Expenditure or not ?'),
        help_text=_(
            'Click on checkbox for general expenditure and don\'t click for investment'),
        default=False
    )

    def __str__(self):
        return f'{self.date} - {self.party} - {self.amount}'


class DailyBalance(TimeStampedModelMixin):

    date = models.DateField(unique=True)
    opening_balance = models.FloatField(_('Opening Balance'))
    closing_balance = models.FloatField(_('Closing Balance'))

    def __str__(self):
        return f'{self.date}'

    def save(self, *args, **kwargs):

        date = self.date
        opening_balance = self.opening_balance

        total_income = Income.objects.filter(date=date).aggregate(
            total=Sum('net_total')).get('total', 0.0)
        total_expense = Expense.objects.filter(date=date).aggregate(
            total=Sum('total_price')).get('total', 0.0)
        investment = Transaction.objects.filter(
            date=date, is_expenditure=False).aggregate(total=Sum('amount')).get('total', 0.0)
        expenditure = Transaction.objects.filter(
            date=date, is_expenditure=True).aggregate(total=Sum('amount')).get('total', 0.0)

        if total_income is None:
            total_income = 0
        if total_expense is None:
            total_expense = 0
        if investment is None:
            investment = 0
        if expenditure is None:
            expenditure = 0

        print(total_income, total_expense, investment, expenditure)

        self.closing_balance = opening_balance + total_income + \
            investment - total_expense - expenditure
        super(DailyBalance, self).save(*args, **kwargs)
