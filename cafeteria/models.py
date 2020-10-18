from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from utils.fields import PercentField
from utils.functions import calculate_percentage
from utils.models import RemarksModelMixin
from utils.models import TimeStampedModelMixin


class CafeteriaManager(TimeStampedModelMixin):

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    joined_date = models.DateField(max_length=255)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        try:
            if_anyone_is_active = CafeteriaManager.objects.get(is_active=True)
            if_anyone_is_active.is_active = False
            super(CafeteriaManager, if_anyone_is_active).save(
                *args, **kwargs)
        except CafeteriaManager.DoesNotExist:
            self.is_active = True
        super(CafeteriaManager, self).save(
            *args, **kwargs)  # Call the real save() method


class Incentive(TimeStampedModelMixin):

    date = models.DateField()
    manager = models.ForeignKey(CafeteriaManager, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f'{self.date} - {self.manager}'


class Particular(TimeStampedModelMixin, RemarksModelMixin):

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




class Income(TimeStampedModelMixin, RemarksModelMixin):

    class Types(models.TextChoices):
        CASH = "CASH", "Cash"
        CREDIT = "CREDIT", "Credit"

    date = models.DateField()
    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    sub_total = models.FloatField()
    discount_amount = models.FloatField(default=0.0)
    discount_percent = PercentField(
        _('Discount Percent'),
        default=0.0
    )
    service_tax = PercentField(
        _('Service Tax Percent'),
        default=0.0
    )
    net_total = models.FloatField()
    is_sold_after_6_pm = models.BooleanField(default=False)
    customer = models.CharField(max_length=255, blank=True, null=True)
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
        self.net_total = self.net_total - self.discount_amount

        try:
            stock_item = Stock.objects.get(particular=self.particular)
            stock_item.item_remaining = stock_item.item_remaining - self.quantity
            stock_item.save()
        except Stock.DoesNotExist:
            pass

        try:
            manager = CafeteriaManager.objects.get(is_active=True)
            if self.is_sold_after_6_pm is True:
                Incentive.objects.create(
                    date=self.date,
                    manager=manager,
                    amount=0.1 * self.net_total
                )
            else:
                pass

        except CafeteriaManager.DoesNotExist:
            pass

        super(Income, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Income / Sale'


class Expense(TimeStampedModelMixin, RemarksModelMixin):

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

        try:
            stock_item = Stock.objects.get(particular=self.particular)
            stock_item.item_remaining = stock_item.item_remaining + self.quantity
            stock_item.save()
        except Stock.DoesNotExist:
            stock_item = Stock()
            stock_item.particular = self.particular
            stock_item.item_remaining = self.quantity
            stock_item.save()

        super(Expense, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Expense / Buying'


class Transaction(TimeStampedModelMixin, RemarksModelMixin):

    date = models.DateField()
    party = models.CharField(max_length=255)
    amount = models.FloatField()
    is_expenditure = models.BooleanField(
        _('Is Expenditure or not ?'),
        help_text=_(
            'Click on checkbox for general expenditure and don\'t click for investment'),
        default=False
    )

    def __str__(self):
        return f'{self.date} - {self.party} - {self.amount}'


class DailyBalance(TimeStampedModelMixin, RemarksModelMixin):

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


class Stock(TimeStampedModelMixin):

    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    item_remaining = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.particular}'


class Credit(TimeStampedModelMixin):

    date = models.DateField()
    transaction = models.OneToOneField(Income, on_delete=models.CASCADE)
    mark_as_cleared = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.transaction}'

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                to_mark_as_clear_sale = Income.objects.get(pk=self.pk)
                to_mark_as_clear_sale.status = Income.Types.CASH
                to_mark_as_clear_sale.save()
            except Income.DoesNotExist:
                pass
        super(Credit, self).save(*args, **kwargs)


class Penalty(TimeStampedModelMixin, RemarksModelMixin):

    date = models.DateField()
    party = models.CharField(max_length=255)
    charge = models.FloatField()
    is_fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.party}'

    class Meta:
        verbose_name = 'Penalty'
        verbose_name_plural = 'Penalties'
