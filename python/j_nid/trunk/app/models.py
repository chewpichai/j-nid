from django.db import models
from django.utils.translation import ugettext as _

class PersonManager(models.Manager):
    def get_query_set(self):
        return super(PersonManager, self).get_query_set().extra(
            select={'num_outstanding_orders': 
                'SELECT COUNT(*) FROM orders WHERE person_id = people.id AND status = 0',
                'outstanding_order_total':
                """SELECT SUM(price_per_unit * unit) FROM order_items WHERE order_id IN 
                (SELECT id FROM orders WHERE person_id = people.id AND status = 0)""",
            }
        )

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True, default='')
    last_name = models.CharField(max_length=255, null=True, blank=True, default='')
    id_card_number = models.CharField(max_length=13, null=True, blank=True, default='')
    address = models.TextField(null=True, blank=True, default='')
    detail1 = models.TextField(null=True, blank=True, default='')
    detail2 = models.TextField(null=True, blank=True, default='')
    objects = PersonManager()
    
    def __unicode__(self):
        return u'%s' % self.name
        
    class Meta:
        db_table = 'people'
        ordering = ['name']

class BankAccount(models.Model):
    BANK_CHOICES = (
        ('BBL', _('BANGKOK BANK')),
        ('SCB', _('SIAM COMMERCIAL BANK')),
        ('KBANK', _('KASIKORN BANK')),
        ('KTB', _('KRUNG THAI BANK')),
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
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        
class ProductType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        db_table = 'product_types'
        ordering = ['name']
        verbose_name = 'product_type'
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProductType, db_column='type', related_name='products')
    unit = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    is_sale = models.BooleanField()
    
    def __unicode__(self):
        return u'%s: %s' % (self.type, self.name)
    
    class Meta:
        db_table = 'products'
        ordering = ['type', 'name']
        unique_together = ('name', 'type')
        
class OrderManager(models.Manager):
    def get_query_set(self):
        return super(OrderManager, self).get_query_set().extra(
            select={'total': 
                'SELECT SUM(price_per_unit * unit) FROM order_items WHERE order_id = orders.id'
            }
        )
        
class Order(models.Model):
    STATUS_OPTIONS = (
        (-1, _('Canceled')),
        (0, _('Outstanding')),
        (1, _('Paid'))
    )
    
    person = models.ForeignKey(Person, related_name='orders')
    notation = models.TextField(null=True, blank=True, default='')
    status = models.IntegerField(choices=STATUS_OPTIONS)
    created = models.DateTimeField(auto_now_add=True)
    objects = OrderManager()
    
    def __unicode__(self):
        return u'Order for %s' % self.person.name
    
    class Meta:
        db_table = 'orders'
        
class OrderItemManager(models.Manager):
    def get_query_set(self):
        return super(OrderItemManager, self).get_query_set().extra(
            select={'total': 'price_per_unit * unit'}
        )
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items')
    product = models.ForeignKey(Product, related_name='order_items')
    price_per_unit = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.PositiveIntegerField()
    objects = OrderItemManager()
    
    def __unicode__(self):
        return u'OrderItem %s' % self.product.name
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'order_item'
