from django.db import models
from django.utils.translation import ugettext as _


class Person(models.Model):
    name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    id_card_number = models.CharField(max_length=13, blank=True, default='')
    address = models.TextField(blank=True, default='')
    detail1 = models.TextField(blank=True, default='')
    detail2 = models.TextField(blank=True, default='')
    type = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'people'

    def __unicode__(self):
        return u'%s' % self.name


class BankAccount(models.Model):
    BANK_CHOICES = (
        ('BBL', _('Bangkok Bank')),
        ('SCB', _('Siam Commercial Bank')),
        ('KBANK', _('Kasikorn Bank')),
        ('KTB', _('Krung Thai Bank')),
    )
    
    person = models.ForeignKey(Person, related_name='bank_accounts')
    number = models.CharField(max_length=10)
    bank = models.CharField(max_length=10, choices=BANK_CHOICES)
    
    class Meta:
        db_table = 'bank_accounts'
        unique_together = ('person', 'number')
        verbose_name = 'bank_account'


class PhoneNumber(models.Model):
    TYPE_CHOICES = (
        ('home', _('Home')),
        ('fax', _('Fax')),
        ('mobile', _('Mobile')),
        ('office', _('Office'))
    )
    
    person = models.ForeignKey(Person, related_name='phone_numbers')
    number = models.CharField(max_length=20)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
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
        unique_together = ('name', 'type')

    def __unicode__(self):
        return u'%s: %s' % (self.type, self.name)


class Order(models.Model):
    person = models.ForeignKey(Person, related_name='orders')
    notation = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders'

    def __unicode__(self):
        return u'Order for %s' % self.person.name   


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
