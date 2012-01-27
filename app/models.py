from django.db import models
from django.utils.translation import ugettext as _
import datetime
import decimal
import math


class Person(models.Model):
    name            = models.CharField(max_length=255, unique=True)
    first_name      = models.CharField(max_length=255, blank=True, default='')
    last_name       = models.CharField(max_length=255, blank=True, default='')
    id_card_number  = models.CharField(max_length=13, blank=True, default='')
    address         = models.TextField(blank=True, default='')
    detail1         = models.TextField(blank=True, default='')
    detail2         = models.TextField(blank=True, default='')
    is_customer     = models.BooleanField()
    is_supplier     = models.BooleanField()
    is_general      = models.BooleanField()
    
    class Meta:
        db_table = 'people'

    def __unicode__(self):
        return u'%s' % self.name
        
    def get_ordered_total(self, start_date=None, end_date=None):
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            return self.orders.filter(created__range=(start_date, end_date)).aggregate(models.Sum('total'))['total__sum'] or 0
        return self.orders.aggregate(models.Sum('total'))['total__sum'] or 0
    ordered_total = property(get_ordered_total)
    
    def get_paid(self, start_date=None, end_date=None):
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            return self.payments.filter(created__range=(start_date, end_date)).aggregate(models.Sum('amount'))['amount__sum'] or 0
        return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
    paid = property(get_paid)
    
    def get_outstanding_total(self):
        return self.paid - self.ordered_total
    outstanding_total = property(get_outstanding_total)
    
    def get_latest_order_date(self):
        return self.orders.latest().created if self.orders.count() else ''
    latest_order_date = property(get_latest_order_date)
    
    def get_num_outstanding_orders(self):
        return len([order for order in self.orders.all() if not order.is_paid])
    num_outstanding_orders = property(get_num_outstanding_orders)
    
    def get_phone_number(self):
        return self.phone_numbers.all()[0].number if self.phone_numbers.count() else ''
    phone_number = property(get_phone_number)
    
    def get_balance_until(self, date):
        payments = self.payments.filter(created__lt=date)
        orders = self.orders.filter(created__lt=date)
        paid = payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        outstanding = orders.aggregate(models.Sum('total'))['total__sum'] or 0
        return paid - outstanding
        
    def get_quantity(self, start_date=None, end_date=None):
        orders = self.orders.extra(select={'quantity':'SELECT SUM(CEIL(order_items.unit/products.unit)) FROM order_items, products WHERE order_items.product_id = products.id AND order_items.order_id = orders.id'})
        if start_date and end_date:
            end_date += datetime.timedelta(1)
            orders = orders.filter(created__range=(start_date, end_date))
        qty = 0
        for order in orders:
            qty += order.quantity
        return qty
    quantity = property(get_quantity)
        

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
        
    def delete(self):
        for basket in self.return_baskets.all():
            basket.is_return = False
            basket.payment = None
            basket.save()
        super(Payment, self).delete()
        
    def get_person_name(self):
        return u'%s' % self.person
    person_name = property(get_person_name)


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
        
    def get_color(self):
        return self.type.color
    color = property(get_color)


class Order(models.Model):
    person      = models.ForeignKey(Person, related_name='orders')
    paid        = models.DecimalField(max_digits=9, decimal_places=2)
    total       = models.DecimalField(max_digits=9, decimal_places=2)
    notation    = models.TextField(blank=True, default='')
    created     = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created']
        get_latest_by = 'created'

    def __unicode__(self):
        return u'Order: %s[%s]' % (self.person.name, self.total)
        
    def save(self, force_insert=False, force_update=False, using=None):
        self.total = self.get_total()
        self.paid = self.get_paid()
        super(Order, self).save(force_insert, force_update)
        
    def get_total(self):
        sum_items = self.order_items.filter(is_deleted=False).aggregate(models.Sum('total'))['total__sum'] or 0
        sum_deposited_baskets = self.order_baskets.filter(is_deposit=True).aggregate(models.Sum('price_per_unit'))['price_per_unit__sum'] or 0
        return sum_items + sum_deposited_baskets
    
    def get_person_name(self):
        return u'%s' % self.person
    person_name = property(get_person_name)
    
    def get_paid(self):
        if not self.created:
            return 0
        orders = self.person.orders.filter(created__lt=self.created)
        sum_ordered = orders.aggregate(models.Sum('total'))['total__sum'] or 0
        paid = self.person.paid - sum_ordered
        return min(max(paid, 0), self.total)
    
    def get_is_paid(self):
        return self.paid == self.total
    is_paid = property(get_is_paid)


class OrderItem(models.Model):
    order           = models.ForeignKey(Order, related_name='order_items')
    product         = models.ForeignKey(Product, related_name='order_items')
    cost_per_unit   = models.DecimalField(max_digits=9, decimal_places=2)
    price_per_unit  = models.DecimalField(max_digits=9, decimal_places=2)
    unit            = models.DecimalField(max_digits=9, decimal_places=2)
    total           = models.DecimalField(max_digits=9, decimal_places=2)
    is_deleted      = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'order_item'

    def __unicode__(self):
        return u'OrderItem %s' % self.product.name
        
    def save(self, force_insert=False, force_update=False, using=None):
        self.total = decimal.Decimal(self.unit) * decimal.Decimal(self.price_per_unit)
        super(OrderItem, self).save(force_insert, force_update)
    
    def get_name(self):
        return u'%s' % self.product.name
    name = property(get_name)
    
    def get_quantity(self):
        return int(max(1, math.ceil(self.unit / self.product.unit)))
    quantity = property(get_quantity)
    
    def get_unit_per_quantity(self):
        return self.product.unit
    unit_per_quantity = property(get_unit_per_quantity)


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
        
    def get_name(self):
        return u'%s' % self.basket.name
    name = property(get_name)
    
    def get_quantity(self):
        return 0
    quantity = property(get_quantity)