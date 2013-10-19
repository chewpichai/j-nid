from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
import datetime
import decimal
import math


class Person(models.Model):
    name                    = models.CharField(max_length=255, unique=True)
    first_name              = models.CharField(max_length=255, blank=True, default='')
    last_name               = models.CharField(max_length=255, blank=True, default='')
    id_card_number          = models.CharField(max_length=13, blank=True, default='')
    address                 = models.TextField(blank=True, default='')
    detail1                 = models.TextField(blank=True, default='')
    detail2                 = models.TextField(blank=True, default='')
    is_customer             = models.BooleanField()
    is_supplier             = models.BooleanField()
    is_general              = models.BooleanField()
    ordered_total           = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    paid                    = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    outstanding_total       = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    num_outstanding_orders  = models.PositiveIntegerField(default=0)
    quantity                = models.PositiveIntegerField(default=0)
    latest_order_date       = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'people'

    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('web.customer_detail', (), {'id': self.id})

    def get_account_url(self):
        today = datetime.date.today()
        start = (today - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
        end = today.strftime('%d-%m-%Y')
        params = '?person=%s&start_date=%s&end_date=%s' % (self.pk, start, end)
        return reverse('web.customer_report') + params

    @property
    def phone_number(self):
        return self.phone_numbers.all()[0].number if self.phone_numbers.count() else ''

    def get_outstanding_total(self):
        return self.paid - self.ordered_total

    def get_latest_order_date(self):
        return self.orders.latest().created if self.orders.count() else None

    def get_ordered_total(self, start_date=None, end_date=None):
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            return self.orders.filter(created__range=(start_date, end_date)).aggregate(models.Sum('total'))['total__sum'] or 0
        return self.orders.aggregate(models.Sum('total'))['total__sum'] or 0

    def get_paid(self, start_date=None, end_date=None):
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            return self.payments.filter(created__range=(start_date, end_date)).aggregate(models.Sum('amount'))['amount__sum'] or 0
        return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0

    def get_num_outstanding_orders(self):
        return len([order for order in self.orders.all() if not order.is_paid])

    def get_balance_until(self, date):
        payments = self.payments.filter(created__lt=date)
        orders = self.orders.filter(created__lt=date)
        paid = payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        outstanding = orders.aggregate(models.Sum('total'))['total__sum'] or 0
        return paid - outstanding

    def get_quantity(self, start_date=None, end_date=None):
        orders = self.orders.all()
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            orders = orders.filter(created__range=(start_date, end_date))
        return orders.aggregate(models.Sum('quantity'))['quantity__sum'] or 0


class Bank(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'banks'
        verbose_name = 'bank'


class BankAccount(models.Model):
    person  = models.ForeignKey(Person, related_name='bank_accounts')
    number  = models.CharField(max_length=20)
    bank    = models.ForeignKey(Bank, related_name='bank_accounts')

    class Meta:
        db_table = 'bank_accounts'
        unique_together = ('person', 'number')
        verbose_name = 'bank_account'


class PhoneType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'phone_types'
        verbose_name = 'phone_type'


class PhoneNumber(models.Model):
    person  = models.ForeignKey(Person, related_name='phone_numbers')
    number  = models.CharField(max_length=20)
    type    = models.ForeignKey(PhoneType, related_name='phone_numbers')

    class Meta:
        db_table = 'phone_numbers'
        unique_together = ('person', 'number')
        verbose_name = 'phone_number'


class Payment(models.Model):
    person      = models.ForeignKey(Person, related_name='payments')
    amount      = models.DecimalField(max_digits=9, decimal_places=2)
    notation    = models.TextField(blank=True, default='')
    created     = models.DateTimeField()

    class Meta:
        db_table = 'payments'
        ordering = ['-created']

    @property
    def person_name(self):
        return u'%s' % self.person


class ProductType(models.Model):
    name    = models.CharField(max_length=255, unique=True)
    color   = models.PositiveIntegerField()

    class Meta:
        db_table = 'product_types'
        verbose_name = 'product_type'

    def __unicode__(self):
        return u'%s' % self.name


class Product(models.Model):
    name            = models.CharField(max_length=255)
    type            = models.ForeignKey(ProductType, db_column='type', related_name='products')
    unit            = models.DecimalField(max_digits=9, decimal_places=2)
    cost_per_unit   = models.DecimalField(max_digits=9, decimal_places=2)
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    is_sale         = models.BooleanField()

    class Meta:
        db_table = 'products'
        ordering = ['type', 'name']
        unique_together = ('name', 'type')

    def __unicode__(self):
        return u'%s: %s' % (self.type, self.name)

    @property
    def color(self):
        return self.type.color

    @property
    def color_hex(self):
        return '#%s' % hex(self.type.color)[2:-1]


class Order(models.Model):
    person      = models.ForeignKey(Person, related_name='orders')
    paid        = models.DecimalField(max_digits=9, decimal_places=2)
    total       = models.DecimalField(max_digits=9, decimal_places=2)
    notation    = models.TextField(blank=True, default='')
    created     = models.DateTimeField()
    quantity    = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'orders'
        ordering = ['-created']
        get_latest_by = 'created'

    def __unicode__(self):
        return u'Order: %s[%s]' % (self.person.name, self.total)

    @property
    def person_name(self):
        return u'%s' % self.person

    @property
    def is_paid(self):
        return self.paid >= self.total

    def get_total(self):
        sum_items = self.order_items.filter(is_deleted=False).aggregate(models.Sum('total'))['total__sum'] or 0
        sum_deposited_baskets = self.order_baskets.filter(is_deposit=True).aggregate(models.Sum('price_per_unit'))['price_per_unit__sum'] or 0
        return sum_items + sum_deposited_baskets

    def get_paid(self):
        if not self.created:
            return 0

        orders = self.person.orders.filter(created__lt=self.created)
        sum_ordered = orders.aggregate(models.Sum('total'))['total__sum'] or 0
        paid = self.person.paid - sum_ordered
        return min(max(paid, 0), self.total)

    def get_quantity(self):
        return self.order_items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0


class OrderItem(models.Model):
    order           = models.ForeignKey(Order, related_name='order_items')
    product         = models.ForeignKey(Product, related_name='order_items')
    cost_per_unit   = models.DecimalField(max_digits=9, decimal_places=2)
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    unit            = models.DecimalField(max_digits=9, decimal_places=2)
    total           = models.DecimalField(max_digits=9, decimal_places=2)
    is_deleted      = models.BooleanField(default=False)
    quantity        = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'order_item'

    def __unicode__(self):
        return u'OrderItem %s' % self.product.name

    @property
    def name(self):
        return u'%s' % self.product.name

    @property
    def unit_per_quantity(self):
        return self.product.unit

    def get_total(self):
        return decimal.Decimal(self.unit) * decimal.Decimal(self.price_per_unit)

    def get_quantity(self):
        return max(1, math.ceil(self.unit / self.product.unit))


class Supply(models.Model):
    person      = models.ForeignKey(Person, related_name='supplies')
    notation    = models.TextField(blank=True, default='')
    created     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supplies'

    def __unicode__(self):
        return u'Supply for %s' % self.person.name


class SupplyItem(models.Model):
    supply          = models.ForeignKey(Supply, related_name='supply_items')
    product         = models.ForeignKey(Product, related_name='supply_items')
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    unit            = models.DecimalField(max_digits=9, decimal_places=2)
    is_deleted      = models.BooleanField(default=False)

    class Meta:
        db_table = 'supply_items'
        verbose_name = 'supply_item'

    def __unicode__(self):
        return u'SupplyItem %s' % self.product.name


class Basket(models.Model):
    name            = models.CharField(max_length=255, unique=True)
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    unit            = models.PositiveIntegerField()
    orders          = models.ManyToManyField(Order, through='BasketOrder', related_name='baskets')
    is_sale         = models.BooleanField()

    class Meta:
        db_table = 'baskets'
        verbose_name = 'basket'

    def __unicode__(self):
        return u'%s' % self.name


class BasketOrder(models.Model):
    basket          = models.ForeignKey(Basket)
    order           = models.ForeignKey(Order, related_name='order_baskets')
    payment         = models.ForeignKey(Payment, related_name='return_baskets', null=True)
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    is_deposit      = models.BooleanField(default=False)
    is_return       = models.BooleanField(default=False)

    class Meta:
        db_table = 'baskets_orders'
        verbose_name = 'basket_order'

    @property
    def name(self):
        return u'%s' % self.basket.name

    @property
    def quantity(self):
        return 0


# ==== Signals ================================================================


@receiver(pre_save, sender=OrderItem, dispatch_uid='orderitem_pre_save')
def orderitem_pre_save(sender, instance, **kwargs):
    instance.total = instance.get_total()
    instance.quantity = instance.get_quantity()


@receiver(post_save, sender=OrderItem, dispatch_uid='orderitem_post_save')
def orderitem_post_save(sender, instance, **kwargs):
    instance.order.save()


@receiver(pre_save, sender=Order, dispatch_uid='order_pre_save')
def order_pre_save(sender, instance, **kwargs):
    instance.total = instance.get_total()
    instance.paid = instance.get_paid()
    instance.quantity = instance.get_quantity()


@receiver(post_save, sender=Order, dispatch_uid='order_post_save')
def order_post_save(sender, instance, **kwargs):
    instance.person.save()


@receiver(post_save, sender=Payment, dispatch_uid='payment_post_save')
def payment_post_save(sender, instance, **kwargs):
    instance.person.save()


@receiver(pre_delete, sender=Payment, dispatch_uid='payment_pre_delete')
def payment_pre_delete(sender, instance, **kwargs):
    for basket in instance.return_baskets.all():
        basket.is_return = False
        basket.payment = None
        basket.save()


@receiver(pre_save, sender=Person, dispatch_uid='person_pre_save')
def person_pre_save(sender, instance, **kwargs):
    instance.ordered_total = instance.get_ordered_total()
    instance.paid = instance.get_paid()
    instance.num_outstanding_orders = instance.get_num_outstanding_orders()
    instance.quantity = instance.get_quantity()
    instance.outstanding_total = instance.get_outstanding_total()
    instance.latest_order_date = instance.get_latest_order_date()
