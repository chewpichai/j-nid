from django.contrib.auth import authenticate, login, logout
from django.db import connection, models, IntegrityError
from django.db.models.query import QuerySet
from django.http import *
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from j_nid.app.models import *
from j_nid.p4x import P4X, toSimpleString
from xml.dom.minidom import getDOMImplementation
from xml.parsers.expat import ExpatError
import datetime
import decimal
import math

def update_model(model, xml):
    for field in model._meta.fields:
        try:
            value = getattr(xml, field.attname)
            if not value:
                continue
            value = toSimpleString(value)
            if isinstance(field, models.BooleanField):
                value = int(value)
            elif isinstance(field, models.CharField):
                value = value or ''
            elif isinstance(field, models.TextField):
                value = value or ''
            elif isinstance(field, models.DateTimeField):
                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            setattr(model, field.attname, value)
        except TypeError:
            continue
    model.save()
    
def model_to_xml(model, attrs=None):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, model._meta.verbose_name, None)
    if not attrs:
        attrs = [attr for attr in model.__dict__ if not attr.startswith('_')]
    for attr in attrs:
        value = getattr(model, attr)
        if isinstance(value, bool):
            value = int(value)
        elif isinstance(value, datetime.datetime):
            value = value.strftime('%a %b %d %H:%M:%S %Y')
        elif isinstance(value, models.Manager):
            if value.count():
                doc.documentElement.appendChild(query_set_to_xml(value.all()).documentElement)
            continue
        elm = doc.createElement(attr)
        elm.appendChild(doc.createTextNode(u'%s' % value))
        doc.documentElement.appendChild(elm)
    return doc
            
def query_set_to_xml(query_set, attrs=None):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, query_set.model._meta.db_table, None)
    for model in query_set:
        doc.documentElement.appendChild(model_to_xml(model, attrs).documentElement)
    return doc
    
def error_xml(*msgs):
    pass
    
def response_xml(data, attrs=None):
    if isinstance(data, QuerySet):
        return HttpResponse(query_set_to_xml(data, attrs).toxml('utf-8'), 
                    mimetype='application/xml')
    return HttpResponse(model_to_xml(data, attrs).toxml('utf-8'), 
                mimetype='application/xml')


class Controller(object):
    def __call__(self, request, **kwargs):
        self.request = request
        method = self.request.method
        self.filters = self.request.GET.get('filters')
        if self.filters:
            try:
                self.filters = dict([f.split('=') for f in self.filters.split(',')])
            except ValueError:
                self.filters = None
        self.attrs = self.request.GET.get('attrs')
        if self.attrs:
            try:
                self.attrs = self.attrs.split(',')
            except ValueError:
                self.attrs = None
        if self.request.raw_post_data:
            try:
                self.xml = P4X(self.request.raw_post_data)
                if self.xml.method:
                    method = toSimpleString(self.xml.method)
            except ExpatError:
                pass
        try:
            callback = getattr(self, 'do_%s' % method)
        except AttributeError:
            return HttpResponseNotFound()
        response = callback(**kwargs)
        response.content_type = 'application/xml'
        return response

    def do_GET(self):
        pass
        
    def do_POST(self):
        pass
        
    def do_PUT(self):
        pass
        
    def do_DELETE(self):
        pass


class SessionController(Controller):
    def do_POST(self):
        username = toSimpleString(self.xml.session.username)
        password = toSimpleString(self.xml.session.password)
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            return HttpResponse()
        else:
            return HttpResponseForbidden()

    def do_DELETE(self):
        logout(self.request)
        return HttpResponse()


class BankController(Controller):
    def do_GET(self):
        banks = Bank.objects.all()
        return response_xml(banks)
    
    
class PhoneTypeController(Controller):
    def do_GET(self):
        phone_types = PhoneType.objects.all()
        return response_xml(phone_types)
    
    
class ProductTypeController(Controller):
    def do_GET(self):
        product_types = ProductType.objects.all()
        if self.filters:
            is_sale = self.filters.get('is_sale')
            if is_sale:
                product_types = product_types.filter(
                    products__is_sale=bool(int(is_sale))).distinct()
        return response_xml(product_types)
        
    def do_POST(self):
        product_type = ProductType()
        try:
            update_model(product_type, self.xml.product_type)
        except IntegrityError:
            return HttpResponse(error_xml('Product type already exist.'),
                        mimetype="application/xml")
        return response_xml(product_type)
        
    def do_PUT(self, id):
        product_type = ProductType.objects.get(id=id)
        update_model(product_type, self.xml.product_type)
        return response_xml(product_type)
    

class ProductController(Controller):
    def do_GET(self):
        products = Product.objects.all()
        if self.filters:
            is_sale = self.filters.get('is_sale')
            if is_sale:
                products = products.filter(is_sale=bool(int(is_sale)));
            type_id = self.filters.get('type_id')
            if type_id:
                products = products.filter(type__id=type_id);
        return response_xml(products, self.attrs)
        
    def do_POST(self):
        product = Product()
        try:
            update_model(product, self.xml.product)
        except IntegrityError:
            return HttpResponse(error_xml('Product already exist.'),
                        mimetype="application/xml")
        return response_xml(product)
        
    def do_PUT(self, id=None):
        if id:
            product = Product.objects.get(id=id)
            update_model(product, self.xml.product)
            return response_xml(product)
        for xml in self.xml.products.product:
            product = Product.objects.get(id=toSimpleString(xml.id))
            update_model(product, xml)
        return HttpResponse()


class PersonController(Controller):
    def do_GET(self, id=None):
        if id:
            person = Person.objects.get(id=id)
            return response_xml(person)
        people = Person.objects.all()
        if self.filters:
            is_customer = self.filters.get('is_customer')
            if is_customer:
                people = people.filter(is_customer=bool(int(is_customer)))
            name = self.filters.get('name')
            if name:
                people = people.filter(name__contains=name)
        return response_xml(people, self.attrs)
        
    def do_POST(self):
        person = Person()
        return self.update_person(person)
                        
    def do_PUT(self, id):
        person = Person.objects.get(id=id)
        return self.update_person(person)
        
    def update_person(self, person):
        try:
            update_model(person, self.xml.person)
        except IntegrityError:
            return HttpResponse(error_xml('Person already exist.'),
                        mimetype="application/xml")
        if self.xml.person.bank_accounts:
            person.bank_accounts.all().delete()
            for ba in self.xml.person.bank_accounts.bank_account:
                bank_account = BankAccount(person=person)
                update_model(bank_account, ba)
        if self.xml.person.phone_numbers:
            person.phone_numbers.all().delete()
            for number in self.xml.person.phone_numbers.phone_number:
                phone_number = PhoneNumber(person=person)
                update_model(phone_number, number)
        doc = model_to_xml(person)
        elm = doc.createElement('bank_accounts')
        for account in person.bank_accounts.all():
            elm.appendChild(model_to_xml(account).documentElement)
        doc.documentElement.appendChild(elm)
        elm = doc.createElement('phone_numbers')
        for number in person.phone_numbers.all():
            elm.appendChild(model_to_xml(number).documentElement)
        doc.documentElement.appendChild(elm)
        return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')


class OrderController(Controller):
    def do_GET(self, id=None):
        if id:
            order = Order.objects.get(id=id)
            return response_xml(order, self.attrs)
        orders = Order.objects.all()
        if self.filters:
            person_id = self.filters.get('person_id')
            if person_id:
                orders = orders.filter(person__id=person_id)
            is_today = self.filters.get('is_today')
            if int(is_today):
                today = datetime.date.today()
                orders = orders.filter(created__gt=today)
            date_range = self.filters.get('date_range')
            if date_range:
                date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                              for d in date_range.split(':')]
                orders = orders.filter(created__range=date_range)
        return response_xml(orders, self.attrs)

    def do_POST(self):
        order = Order()
        return self.update_order(order)
        
    def do_PUT(self, id):
        order = Order.objects.get(id=id)
        return self.update_order(order)

    def do_DELETE(self, id):
        order = Order.objects.get(id=id)
        person = order.person
        amount = order.paid
        order.delete()
        for o in person.orders.extra(where=['paid <> total']).order_by('created'):
            if amount <= 0:
                break
            amount -= order.total - order.paid
            o.save()
        return HttpResponse('<id>%s</id>' % id, mimetype='application/xml')
        
    def update_order(self, order):
        is_edit = False
        if order.id:
            is_edit = True
        before_total = order.total
        update_model(order, self.xml.order)
        for item in self.xml.order.order_items.order_item:
            if item.id:
                order_item = order.order_items.get(id=toSimpleString(item.id))
            else:
                order_item = OrderItem(order=order)
            update_model(order_item, item)
        order.order_baskets.filter(is_deposit=False).delete()
        if self.xml.order.non_deposit_baskets and self.xml.order.non_deposit_baskets.basket:
            for non_deposit_basket in self.xml.order.non_deposit_baskets.basket:
                basket = Basket.objects.get(id=toSimpleString(non_deposit_basket.id))
                for i in range(int(toSimpleString(non_deposit_basket.unit))):
                    BasketOrder.objects.create(basket=basket, order=order,
                        price_per_unit=toSimpleString(non_deposit_basket.price_per_unit))
        order.order_baskets.filter(is_deposit=True).delete()
        if self.xml.order.deposited_baskets and self.xml.order.deposited_baskets.basket:
            for deposited_basket in self.xml.order.deposited_baskets.basket:
                basket = Basket.objects.get(id=toSimpleString(deposited_basket.id))
                for i in range(int(toSimpleString(deposited_basket.unit))):
                    BasketOrder.objects.create(basket=basket, order=order, is_deposit=True,
                        price_per_unit=toSimpleString(deposited_basket.price_per_unit))
        order.save()
        after_total = order.total
        if is_edit:
            diff_total = before_total - after_total
            if diff_total < 0:
                diff_total = abs(diff_total)
                for o in order.person.orders.filter(paid__gt=0):
                    if diff_total <= 0:
                        break
                    if int(o.id) != int(order.id):
                        diff_total -= o.paid
                    o.save()
            elif diff_total > 0:
                for o in order.person.orders.extra(where=['paid <> total']).order_by('created'):
                    if diff_total <= 0:
                        break
                    if int(o.id) != int(order.id):
                        diff_total -= o.total - o.paid
                    o.save()
        if self.xml.order.paid:
            created = order.created + datetime.timedelta(seconds=30)
            payment = Payment.objects.create(person=order.person,
                amount=toSimpleString(self.xml.order.paid), created=created)
            amount = decimal.Decimal(payment.amount)
            for o in order.person.orders.extra(where=['paid <> total']).order_by('created'):
                if amount <= 0:
                    break
                amount -= o.total - o.paid
                o.save()
        doc = model_to_xml(order)
        elm = doc.createElement('order_items')
        for item in order.order_items.all():
            elm.appendChild(model_to_xml(item).documentElement)
        doc.documentElement.appendChild(elm)
        return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')


class OrderItemController(Controller):
    def do_GET(self):
        order_items = OrderItem.objects.all()
        if self.filters:
            order_id = self.filters.get('order_id')
            if order_id:
                order_items = order_items.filter(order__id=order_id)
        return response_xml(order_items, self.attrs)

    def do_POST(self):
        order_item = OrderItem()
        update_model(order_item, self.xml.order_item)
        return response_xml(order_item)
        
    def do_PUT(self, id):
        order_item = OrderItem.objects.get(id=id)
        update_model(order_item, self.xml.order_item)
        return response_xml(order_item)

    def do_DELETE(self, id):
        order_item = OrderItem.objects.get(id=id)
        order_item.is_deleted = True
        order_item.save()
        order_item.order.save()
        return HttpResponse('<id>%s</id>' % id, mimetype='application/xml')


class BankAccountController(Controller):
    def do_GET(self):
        bank_accounts = BankAccount.objects.all()
        return response_xml(bank_accounts)

    def do_POST(self):
        bank_account = BankAccount()
        update_model(bank_account, self.xml.bank_account)
        return response_xml(bank_account)
        
    def do_PUT(self):
        bank_account = BankAccount.objects.get(id=id)
        update_model(bank_account, self.xml.bank_account)
        return response_xml(bank_account)

    def do_DELETE(self, id):
        bank_account = BankAccount.objects.get(id=id)
        bank_account.delete()
        return HttpResponse('<id>%s</id>' % id)


class PhoneNumberController(Controller):
    def do_GET(self):
        phone_numbers = PhoneNumber.objects.all()
        return response_xml(phone_numbers)

    def do_POST(self):
        phone_number = PhoneNumber()
        update_model(phone_number, self.xml.phone_number)
        return response_xml(phone_number)
        
    def do_POST(self, id):
        phone_number = PhoneNumber.objects.get(id=id)
        update_model(phone_number, self.xml.phone_number)
        return response_xml(phone_number)

    def do_DELETE(self, id):
        phone_number = PhoneNumber.objects.get(id=id)
        phone_number.delete()
        return HttpResponse('<id>%s</id>' % id)


class PaymentController(Controller):
    def do_GET(self, id=None, person_id=None):
        if id:
            payment = Payment.objects.get(id=id)
            return response_xml(payment, self.attrs)
        if int(person_id):
            payments = Payment.objects.filter(person__id=person_id)
        else:
            payments = Payment.objects.all()
        if self.filters:
            date_range = self.filters.get('date_range')
            if date_range:
                date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                              for d in date_range.split(':')]
                payments = payments.filter(created__range=date_range)
        return response_xml(payments)
        
    def do_POST(self):
        payment = Payment()
        update_model(payment, self.xml.payment)
        if self.xml.payment.basket_orders and self.xml.payment.basket_orders.basket_order:
            for xml in self.xml.payment.basket_orders.basket_order:
                basket_order = BasketOrder.objects.get(id=toSimpleString(xml.id))
                update_model(basket_order, xml)
                basket_order.payment = payment
                basket_order.save()
        amount = decimal.Decimal(payment.amount)
        for order in payment.person.orders.extra(where=['paid <> total']).order_by('created'):
            if amount <= 0:
                break
            amount -= order.total - order.paid
            order.save()
        return response_xml(payment)
        
    def do_PUT(self, id):
        payment = Payment.objects.get(id=id)
        update_model(payment, self.xml.payment)
        return response_xml(payment)

    def do_DELETE(self, id):
        payment = Payment.objects.get(id=id)
        person = payment.person
        amount = payment.amount
        payment.delete()
        for order in person.orders.filter(paid__gt=0):
            if amount <= 0:
                break
            amount -= order.paid
            order.save()
        return HttpResponse('<id>%s</id>' % id, mimetype='application/xml')


class SupplyController(Controller):
    def do_GET(self):
        supplies = Supply.objects.all()
        return response_xml(supplies)

    def do_POST(self):
        supply = Supply()
        update_model(supply, self.xml.supply)
        for item in self.xml.supply.supply_items.supply_item:
            supply_item = SupplyItem()
            update_model(supply_item, item)
            supply.supply_items.add(supply_item)
        doc = model_to_xml(supply)
        elm = doc.createElement('supply_items')
        for item in supply.supply_items.all():
            elm.appendChild(model_to_xml(item).documentElement)
        doc.documentElement.appendChild(elm)
        return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')
        
    def do_PUT(self, id):
        supply = Supply.objects.get(id=id)
        update_model(supply, self.xml.supply)
        return response_xml(supply)

    def do_DELETE(self, id):
        supply = Supply.objects.get(id=id)
        supply.delete()
        return HttpResponse('<id>%s</id>' % id, mimetype='application/xml')


class SupplyItemController(Controller):
    def do_GET(self):
        supply_items = SupplyItem.objects.all()
        return response_xml(supply_items)

    def do_POST(self):
        supply_item = SupplyItem()
        update_model(supply_item, self.xml.supply_item)
        return response_xml(supply_item)
        
    def do_PUT(self, id):
        supply_item = SupplyItem.objects.get(id=id)
        update_model(supply_item, self.xml.supply_item)
        return response_xml(supply_item)

    def do_DELETE(self, id):
        supply_item = SupplyItem.objects.get(id=id)
        supply_item.is_deleted = True
        supply_item.save()
        return HttpResponse('<id>%s</id>' % id, mimetype='application/xml')
        
        
class BasketController(Controller):
    def do_GET(self):
        baskets = Basket.objects.all()
        if self.filters:
            is_sale = self.filters.get('is_sale')
            if is_sale:
                baskets = baskets.filter(is_sale=bool(int(is_sale)));
        return response_xml(baskets)
        
    def do_POST(self):
        basket = Basket()
        update_model(basket, self.xml.basket)
        return response_xml(basket)
        
    def do_PUT(self, id):
        basket = Basket.objects.get(id=id)
        update_model(basket, self.xml.basket)
        return response_xml(basket)
        
class BasketOrderController(Controller):
    def do_GET(self, order_id=None, person_id=None, payment_id=None):
        baskets_orders = BasketOrder.objects.all()
        if order_id:
            baskets_orders = baskets_orders.filter(order__id=order_id)
        if person_id:
            baskets_orders = baskets_orders.filter(order__person__id=person_id)
        if payment_id:
            baskets_orders = baskets_orders.filter(payment__id=payment_id)
        if self.filters:
            is_return = self.filters.get('is_return')
            baskets_orders = baskets_orders.filter(is_return=bool(int(is_return)))
        return response_xml(baskets_orders, self.attrs)
        
    def do_PUT(self):
        for xml in self.xml.basket_orders.basket_order:
            basket_order = BasketOrder.objects.get(id=toSimpleString(xml.id))
            update_model(basket_order, xml)
        return HttpResponse()
        
def get_transactions(request):
    orders = Order.objects.all()
    payments = Payment.objects.all()
    transactions = []
    filters = request.GET.get('filters')
    if filters:
        filters = dict([f.split('=') for f in filters.split(',')])
        person_id = filters.get('person_id')
        if person_id:
            orders = orders.filter(person=person_id)
            payments = payments.filter(person=person_id)
        date_range = filters.get('date_range')
        if date_range:
            date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                              for d in date_range.split(':')]
            orders = orders.filter(created__range=date_range)
            payments = payments.filter(created__range=date_range)
    orders = orders.extra(select={'quantity':'SELECT SUM(CEIL(order_items.unit/products.unit)) FROM order_items, products WHERE order_items.product_id = products.id AND order_items.order_id = orders.id'})
    for order in orders:
        transactions.append(Transaction(order))
    for payment in payments:
        transactions.append(Transaction(payment))
    transactions.sort()
    transactions.reverse()
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'transactions', None)
    for transaction in transactions:
        doc.documentElement.appendChild(transaction.to_xml().documentElement)
    return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')
        
def get_person_transactions(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    orders = person.orders.all()
    payments = person.payments.all()
    transactions = []
    balance = 0
    filters = request.GET.get('filters')
    if filters:
        filters = dict([f.split('=') for f in filters.split(',')])
        date_range = filters.get('date_range')
        if date_range:
            date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                          for d in date_range.split(':')]
            balance = person.get_balance_until(date_range[0])
            if balance:
                obj = {'created': date_range[0], 'balance': balance}
                transactions.append(Transaction(obj))
            orders = orders.filter(created__range=date_range)
            payments = payments.filter(created__range=date_range)
    for order in orders:
        transactions.append(Transaction(order))
    for payment in payments:
        transactions.append(Transaction(payment))
    transactions.sort()
    for transaction in transactions:
        if transaction.type != 'balance':
            transaction.balance += balance
            balance = transaction.balance
    transactions.reverse()
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'transactions', None)
    for transaction in transactions:
        doc.documentElement.appendChild(transaction.to_xml().documentElement)
    return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')
    
def get_products_stats(request):
    orders = Order.objects.all()
    filters = request.GET.get('filters')
    if filters:
        filters = dict([f.split('=') for f in filters.split(',')])
        person_id = filters.get('person_id')
        if person_id:
            orders = orders.filter(person=person_id)
        date_range = filters.get('date_range')
        if date_range:
            date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                          for d in date_range.split(':')]
            orders = orders.filter(created__range=date_range)
    products = Product.objects.filter(order_items__order__in=orders).distinct()
    order_items = OrderItem.objects.filter(order__in=orders)
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'product_stats', None)
    for product in products:
        product_stat = impl.createDocument(None, 'product_stat', None)
        id = product_stat.createElement('id')
        id.appendChild(product_stat.createTextNode(u'%s' % product.id))
        product_stat.documentElement.appendChild(id)
        units = product_stat.createElement('unit')
        unit_sum = order_items.filter(product=product).aggregate(models.Sum('unit'))['unit__sum']
        units.appendChild(product_stat.createTextNode(u'%s' % unit_sum))
        product_stat.documentElement.appendChild(units)
        name = product_stat.createElement('name')
        name.appendChild(product_stat.createTextNode(u'%s' % product.name))
        product_stat.documentElement.appendChild(name)
        quantity = product_stat.createElement('quantity')
        quantity.appendChild(product_stat.createTextNode(u'%s' % math.ceil(unit_sum / product.unit)))
        product_stat.documentElement.appendChild(quantity)
        doc.documentElement.appendChild(product_stat.documentElement)
    return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')
    
def get_products_stats_detail(request):
    product_ids = request.GET.get('product_ids').split(',')
    date_range = request.GET.get('date_range')
    person_id = int(request.GET.get('person_id', 0))
    products_stats = [get_product_stats_data(id, person_id, date_range) for id in product_ids]
    return render_to_response('products_stats.xml', {'products_stats': products_stats}, mimetype='application/xml')
    
def get_people_summary(request):
    people = Person.objects.filter(id__gt=24)
    date_range = request.GET.get('date_range')
    if date_range:
        date_range = [datetime.datetime.strptime(d, '%Y%m%d')
                      for d in date_range.split(':')]
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'people', None)
    for person in people:
        ordered_total = person.get_ordered_total(*date_range) if date_range else person.ordered_total
        paid = person.get_paid(*date_range) if date_range else person.paid
        if ordered_total and paid:
            person_doc = impl.createDocument(None, 'person', None)
            name_elmt = person_doc.createElement('name')
            name_elmt.appendChild(person_doc.createTextNode(person.name))
            person_doc.documentElement.appendChild(name_elmt)
            quantity_elmt = person_doc.createElement('quantity')
            quantity = person.get_quantity(*date_range) if date_range else person.quantity
            quantity_elmt.appendChild(person_doc.createTextNode(u'%s' % quantity))
            person_doc.documentElement.appendChild(quantity_elmt)
            ordered_total_elmt = person_doc.createElement('ordered_total')
            ordered_total_elmt.appendChild(person_doc.createTextNode(u'%s' % ordered_total))
            person_doc.documentElement.appendChild(ordered_total_elmt)
            paid_elmt = person_doc.createElement('paid')
            paid_elmt.appendChild(person_doc.createTextNode(u'%s' % paid))
            person_doc.documentElement.appendChild(paid_elmt)
            outstanding_total = paid - ordered_total
            outstanding_total_elmt = person_doc.createElement('outstanding_total')
            outstanding_total_elmt.appendChild(person_doc.createTextNode(u'%s' % outstanding_total))
            person_doc.documentElement.appendChild(outstanding_total_elmt)
            doc.documentElement.appendChild(person_doc.documentElement)
    return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')

class Transaction(object):
    def __init__(self, obj):
        if isinstance(obj, models.Model):
            self.id = obj.id
            self.person_name = obj.person.name
            self.type = obj._meta.verbose_name
            self.created = obj.created
            self.quantity = getattr(obj, 'quantity', '')
            self.outstanding = getattr(obj, 'total', 0)
            self.paid = getattr(obj, 'amount', 0)
            self.note = obj.notation
            self.balance = self.paid - self.outstanding
        else:
            self.type = 'balance'
            self.created = obj['created']
            self.outstanding = 0
            self.paid = 0
            self.note = u'ยอดยกมา'
            self.balance = obj['balance']
        
    def __cmp__(self, other):
        if self.created < other.created:
            return -1
        elif self.created == other.created:
            return 0
        elif self.created > other.created:
            return 1
        
    def to_xml(self):
        impl = getDOMImplementation()
        doc = impl.createDocument(None, 'transaction', None)
        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if callable(value):
                    continue
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%a %b %d %H:%M:%S %Y')
                elm = doc.createElement(attr)
                elm.appendChild(doc.createTextNode(u'%s' % value))
                doc.documentElement.appendChild(elm)
        return doc
        
def get_monthly_report(request, year, month):
    reports = {}
    cursor = connection.cursor()
    cursor.execute('SELECT SUM(total), DATE(created) FROM orders WHERE YEAR(created) = %s AND MONTH(created) = %s GROUP BY DATE(created)', [year, month])
    for (ordered_total, created) in cursor.fetchall():
        reports.setdefault(created, {})['ordered_total'] = ordered_total
    cursor.execute('SELECT SUM(amount), DATE(created) FROM payments WHERE YEAR(created) = %s AND MONTH(created) = %s GROUP BY DATE(created)', [year, month])
    for (paid_total, created) in cursor.fetchall():
        reports.setdefault(created, {})['paid_total'] = paid_total
    cursor.execute('SELECT SUM(CEIL(order_items.unit / products.unit)), DATE(created) FROM order_items INNER JOIN orders ON orders.id = order_items.order_id INNER JOIN products ON order_items.product_id = products.id WHERE YEAR(created) = %s AND MONTH(created) = %s GROUP BY DATE(created)', [year, month])
    for (quantity, created) in cursor.fetchall():
        reports.setdefault(created, {})['quantity'] = quantity
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'reports', None)
    keys = reports.keys()
    keys.sort()
    for created in keys:
        report = reports[created]
        report['outstanding_total'] = report.get('paid_total', 0) - report.get('ordered_total', 0)
        report_doc = impl.createDocument(None, 'report', None)
        created_elmt = report_doc.createElement('created')
        created_elmt.appendChild(report_doc.createTextNode(u'%s' % created.strftime('%a %b %d %H:%M:%S %Y')))
        report_doc.documentElement.appendChild(created_elmt)
        for attr, val in report.items():
            elmt = report_doc.createElement(attr)
            elmt.appendChild(report_doc.createTextNode(u'%s' % val))
            report_doc.documentElement.appendChild(elmt)
        doc.documentElement.appendChild(report_doc.documentElement)
    return HttpResponse(doc.toxml('utf-8'), mimetype='application/xml')

def get_year_list(request):
    years = []
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT(YEAR(created)) FROM orders ORDER BY created DESC')
    for (year,) in cursor.fetchall():
        years.append(year)
    return render_to_response('year_list.xml', {'years': years}, mimetype='application/xml')

def get_month_list(request, year):
    months = []
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT(MONTH(created)) FROM orders WHERE YEAR(created) = %s ORDER BY created DESC', [year])
    for (month,) in cursor.fetchall():
        months.append(month)
    return render_to_response('month_list.xml', {'months': months}, mimetype='application/xml')
    
def get_product_stats(request, id):
    date_range = request.GET.get('date_range')
    person_id = int(request.GET.get('person_id', 0))
    data = get_product_stats_data(id, person_id, date_range)
    return render_to_response('product_stats.xml', data, mimetype='application/xml')
    
def get_product_stats_data(product_id, person_id, date_range):
    cursor = connection.cursor()
    if date_range:
        date_range = [datetime.datetime.strptime(d, '%Y%m%d') for d in date_range.split(':')]
        if person_id:
            cursor.execute('SELECT products.name, CEIL(SUM(order_items.unit)/products.unit), order_items.price_per_unit FROM order_items INNER JOIN products ON order_items.product_id = products.id INNER JOIN orders ON order_items.order_id = orders.id WHERE orders.person_id = %s AND products.id = %s AND created BETWEEN %s AND %s GROUP BY products.id, order_items.price_per_unit', [person_id, product_id, date_range[0], date_range[1]])
        else:
            cursor.execute('SELECT products.name, CEIL(SUM(order_items.unit)/products.unit), order_items.price_per_unit FROM order_items INNER JOIN products ON order_items.product_id = products.id INNER JOIN orders ON order_items.order_id = orders.id WHERE products.id = %s AND created BETWEEN %s AND %s GROUP BY products.id, order_items.price_per_unit', [product_id, date_range[0], date_range[1]])
    else:
        if person_id:
            cursor.execute('SELECT products.`name`, CEIL(SUM(order_items.unit)/products.unit), order_items.price_per_unit FROM order_items INNER JOIN products ON order_items.product_id = products.id INNER JOIN orders ON order_items.order_id = orders.id WHERE orders.person_id = %s AND products.id = %s GROUP BY products.id, order_items.price_per_unit', [person_id, product_id])
        else:
            cursor.execute('SELECT products.`name`, CEIL(SUM(order_items.unit)/products.unit), order_items.price_per_unit FROM order_items INNER JOIN products ON order_items.product_id = products.id INNER JOIN orders ON order_items.order_id = orders.id WHERE products.id = %s GROUP BY products.id, order_items.price_per_unit', [product_id])
    stats = []
    for (name, quantity, price_per_unit) in cursor.fetchall():
        stats.append({'quantity': quantity, 'price_per_unit': price_per_unit})
    return {'name': name, 'stats': stats}
    