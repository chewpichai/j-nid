from django.db import models
from django.utils.translation import ugettext as _


class Person(models.Model):
    GENERAL_TYPE = 0;
    CUSTOMER_TYPE = 1;
    SUPPLIER_TYPE = 2;
    
    name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    id_card_number = models.CharField(max_length=13, blank=True, default='')
    address = models.TextField(blank=True, default='')
    detail1 = models.TextField(blank=True, default='')
    detail2 = models.TextField(blank=True, default='')
    is_customer = models.BooleanField()
    is_supplier = models.BooleanField()
    is_general = models.BooleanField()
    
    class Meta:
        db_table = 'people'

    def __unicode__(self):
        return u'%s' % self.name
        
    def get_ordered_total(self):
        orders = self.orders.all()
        return reduce(lambda x,y: x+y, [order.total for order in orders]) if orders else 0
    ordered_total = property(get_ordered_total)
    
    def get_paid(self):
        sum = self.payments.aggregate(models.Sum('amount'))['amount__sum']
        return sum or 0
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
        outstanding = reduce(lambda x,y: x+y, [order.total for order in orders]) if orders else 0
        return paid - outstanding
        
        
class Bank(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = 'banks'
        verbose_name = 'bank'


class BankAccount(models.Model):
    person = models.ForeignKey(Person, related_name='bank_accounts')
    number = models.CharField(max_length=20)
    bank = models.ForeignKey(Bank, related_name='bank_accounts')
    
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
    person = models.ForeignKey(Person, related_name='phone_numbers')
    number = models.CharField(max_length=20)
    type = models.ForeignKey(PhoneType, related_name='phone_numbers')
    
    class Meta:
        db_table = 'phone_numbers'
        unique_together = ('person', 'number')
        verbose_name = 'phone_number'


class Payment(models.Model):
    person = models.ForeignKey(Person, related_name='payments')
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    notation = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created']


class ProductType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    color = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'product_types'
        verbose_name = 'product_type'

    def __unicode__(self):
        return u'%s' % self.name

    
class Product(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProductType, db_column='type',
                        related_name='products')
    unit = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    is_sale = models.BooleanField()
    
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
    person = models.ForeignKey(Person, related_name='orders')
    notation = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created']
        get_latest_by = 'created'

    def __unicode__(self):
        return u'Order: %s[%s]' % (self.person.name, self.total)
        
    def get_total(self):
        order_items = self.order_items.all()
        sum_items = reduce(lambda x,y: x+y, [i.total for i in order_items]) if order_items else 0
        pledge_baskets = self.order_baskets.filter(is_pledge=True)
        sum_pledge_baskets = reduce(lambda x,y: x+y, [b.price_per_unit for b in pledge_baskets]) if pledge_baskets else 0
        return sum_items + sum_pledge_baskets
    total = property(get_total)
    
    def get_person_name(self):
        return u'%s' % self.person
    person_name = property(get_person_name)
    
    def get_paid(self):
        total = self.total
        orders = list(self.person.orders.filter(created__lte=self.created))
        orders.remove(self)
        sum = reduce(lambda x,y: x+y, [order.total for order in orders]) if orders else 0
        paid = self.person.paid - sum
        return max(paid, 0) if paid - total < 0 else total
    paid = property(get_paid)
    
    def get_is_paid(self):
        return self.paid == self.total
    is_paid = property(get_is_paid)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items')
    product = models.ForeignKey(Product, related_name='order_items')
    cost_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    unit = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'order_item'

    def __unicode__(self):
        return u'OrderItem %s' % self.product.name
        
    def get_total(self):
        return self.unit * self.price_per_unit
    total = property(get_total)
    
    def get_name(self):
        return u'%s' % self.product.name
    name = property(get_name)
    
    def get_quantity(self):
        return int(max(1, round(self.unit / self.product.unit)))
    quantity = property(get_quantity)
    
    def get_unit_per_quantity(self):
        return self.product.unit
    unit_per_quantity = property(get_unit_per_quantity)


class Supply(models.Model):
    person = models.ForeignKey(Person, related_name='supplies')
    notation = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supplies'

    def __unicode__(self):
        return u'Supply for %s' % self.person.name


class SupplyItem(models.Model):
    supply = models.ForeignKey(Supply, related_name='supply_items')
    product = models.ForeignKey(Product, related_name='supply_items')
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    unit = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'supply_items'
        verbose_name = 'supply_item'

    def __unicode__(self):
        return u'SupplyItem %s' % self.product.name
        
class Basket(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    unit = models.PositiveIntegerField()
    orders = models.ManyToManyField(Order, through='BasketOrder',
                related_name='baskets')
    is_sale = models.BooleanField()

    class Meta:
        db_table = 'baskets'
        verbose_name = 'basket'
        
    def __unicode__(self):
        return u'%s' % self.name
        
        
class BasketOrder(models.Model):
    basket = models.ForeignKey(Basket)
    order = models.ForeignKey(Order, related_name='order_baskets')
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    is_pledge = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'baskets_orders'
        verbose_name = 'basket_order'
        
    def get_name(self):
        return u'%s' % self.basket.name
    name = property(get_name)
    
    def get_quantity(self):
        return 0
    quantity = property(get_quantity)
        