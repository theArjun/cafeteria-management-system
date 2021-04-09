from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from utils.fields import PercentField
from utils.functions import calculate_percentage
from utils.models import (
    RemarksModelMixin,
    TimeStampedModelMixin,
)


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
            super(CafeteriaManager, if_anyone_is_active).save(*args, **kwargs)
        except CafeteriaManager.DoesNotExist:
            self.is_active = True
        super(CafeteriaManager,
              self).save(*args, **kwargs)  # Call the real save() method


class Customer(TimeStampedModelMixin, RemarksModelMixin):
    name = models.CharField(_('Customer Name'), max_length=255)
    reserve_balance = models.FloatField(_('Reserve Balance'), default=0)
    phone_number = models.CharField(
        _('Phone Number'), max_length=15, default='', blank=True
    )
    credit_balance = models.FloatField(_('Credit Balance'), default=0.0)

    def save(self, *args, **kwargs):
        if self.credit_balance >= self.reserve_balance:
            difference = self.credit_balance - self.reserve_balance
            self.reserve_balance = 0
            self.credit_balance = self.credit_balance - difference
        else:
            difference = self.reserve_balance - self.credit_balance
            self.credit_balance = 0
            self.reserve_balance = difference
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Particular(TimeStampedModelMixin, RemarksModelMixin):
    class Purpose(models.TextChoices):
        INPUT = 'INPUT', 'Input'
        OUTPUT = 'OUTPUT', 'Output'
        BOTH = 'BOTH', 'Both'

    particular = models.CharField(max_length=255)
    cost_unit_price = models.FloatField()
    selling_unit_price = models.FloatField()
    bought_for = models.CharField(_('Purpose'),
                                  max_length=50,
                                  choices=Purpose.choices,
                                  default=Purpose.OUTPUT)

    def __str__(self):
        return f'{self.particular}'


class Income(TimeStampedModelMixin, RemarksModelMixin):
    class Types(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CREDIT = 'CREDIT', 'Credit'
        RESERVE = 'RESERVE', 'Reserve'

    date = models.DateField()
    discount_amount = models.FloatField(default=0.0)
    discount_percent = PercentField(_('Discount Percent'), default=0.0)
    service_tax = PercentField(_('Service Tax Percent'), default=0.0)
    customer = models.ForeignKey(Customer,
                                 on_delete=models.DO_NOTHING,
                                 blank=True,
                                 null=True)
    status = models.CharField(_('Status'),
                              max_length=50,
                              choices=Types.choices,
                              default=Types.CASH)

    def __str__(self):
        return f'{self.date} - {self.customer}'

    class Meta:
        verbose_name = 'Income / Sale'


class SaleItem(models.Model):
    '''Model definition for SaleItem.'''

    sale = models.ForeignKey(
        Income,
        verbose_name=_('Sale Item'),
        on_delete=models.CASCADE,
        related_name='sales',
        related_query_name='sales',
    )
    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    total = models.FloatField(_('Total for Sale Item'))

    class Meta:
        '''Meta definition for SaleItem.'''

        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        '''Unicode representation of SaleItem.'''
        return f'{self.particular} ({self.quantity})'

    def save(self, *args, **kwargs):

        self.total = self.particular.selling_unit_price * self.quantity
        super(SaleItem, self).save(*args, **kwargs)


class Expense(TimeStampedModelMixin, RemarksModelMixin):
    class Types(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CREDIT = 'CREDIT', 'Credit'

    date = models.DateField()
    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    total_price = models.FloatField()
    bought_by = models.CharField(max_length=255)
    bought_from = models.CharField(max_length=255)
    status = models.CharField(_('Status'),
                              max_length=50,
                              choices=Types.choices,
                              default=Types.CASH)

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
    is_outgoing = models.BooleanField(
        _('Outgoing Balance ?'),
        help_text=
        _('Click on checkbox for general expenditure and don\'t click for investment'
          ),
        default=False)

    def __str__(self):
        return f'{self.date} - {self.party} - {self.amount}'


class DailyBalance(TimeStampedModelMixin, RemarksModelMixin):

    date = models.DateField(unique=True)
    opening_balance = models.FloatField(_('Opening Balance'))

    def __str__(self):
        return f'{self.date}'


class Stock(TimeStampedModelMixin):

    particular = models.ForeignKey(Particular, on_delete=models.CASCADE)
    item_remaining = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.particular}'


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
