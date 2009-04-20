from django.db import models, IntegrityError
from django.db.models.fields.related import RelatedField
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from j_nid.app.models import *
from p4x import P4X
from xml.dom.minidom import getDOMImplementation
from xml.parsers.expat import ExpatError
import datetime

def get_banks(request):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'banks', None)
    for data, label in BankAccount.BANK_CHOICES:
        elm = doc.createElement('bank')
        labelEml = doc.createElement('label')
        dataEml = doc.createElement('data')
        labelEml.appendChild(doc.createTextNode(u'%s' % label))
        dataEml.appendChild(doc.createTextNode(u'%s' % data))
        elm.appendChild(labelEml)
        elm.appendChild(dataEml)
        doc.documentElement.appendChild(elm)
    return HttpResponse(doc.toxml('utf-8'), mimetype="application/xml")
    
def get_phonetypes(request):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'phone_types', None)
    for data, label in PhoneNumber.TYPE_CHOICES:
        elm = doc.createElement('phone_type')
        labelEml = doc.createElement('label')
        dataEml = doc.createElement('data')
        labelEml.appendChild(doc.createTextNode(u'%s' % label))
        dataEml.appendChild(doc.createTextNode(u'%s' % data))
        elm.appendChild(labelEml)
        elm.appendChild(dataEml)
        doc.documentElement.appendChild(elm)
    return HttpResponse(doc.toxml('utf-8'), mimetype="application/xml")

def update_model(model, xml):
    for field in model._meta.fields:
        name = field.attname
        try:
            value = getattr(xml, name)[0].value
            if isinstance(field, models.BooleanField):
                value = int(value)
            elif isinstance(field, models.CharField):
                value = value or ''
            elif isinstance(field, models.TextField):
                value = value or ''
            setattr(model, name, value)
        except TypeError:
            continue
    model.save()
    
def model_to_xml(model):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, model._meta.verbose_name, None)
    for attr in model.__dict__:
        if not attr.startswith('_'):
            value = model.__dict__[attr]
            if isinstance(value, bool):
                value = int(value)
            elif isinstance(value, datetime.datetime):
                value = value.strftime('%a %b %d %H:%M:%S %Y')
            elm = doc.createElement(attr)
            elm.appendChild(doc.createTextNode(u'%s' % value))
            doc.documentElement.appendChild(elm)
    return doc
            
def query_set_to_xml(query_set):
    impl = getDOMImplementation()
    doc = impl.createDocument(None, query_set.model._meta.db_table, None)
    for model in query_set:
        doc.documentElement.appendChild(model_to_xml(model).documentElement)
    return doc
    
def error_xml(*msgs):
    pass
    
def response_xml(data):
    if isinstance(data, QuerySet):
        return HttpResponse(query_set_to_xml(data).toxml('utf-8'), mimetype='application/xml')
    return HttpResponse(model_to_xml(data).toxml('utf-8'), mimetype='application/xml')


class Controller(object):
    def __call__(self, request, **kwargs):
        self.request = request
        self.params = request.REQUEST
        method = request.method
        if request.raw_post_data:
            try:
                self.xml = P4X(self.request.raw_post_data)
                if self.xml.method:
                    method = self.xml.method[0].value
            except ExpatError:
                pass
        try:
            callback = getattr(self, 'do_%s' % method)
        except AttributeError:
            return HttpResponseNotFound()
        return callback(**kwargs)

    def do_GET(self):
        pass
        
    def do_POST(self):
        pass
        
    def do_PUT(self):
        pass
        
    def do_DELETE(self):
        pass


class ProductTypeController(Controller):
    def do_GET(self):
        product_types = ProductType.objects.all()
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
        return response_xml(products)
        
    def do_POST(self):
        product = Product()
        try:
            update_model(product, self.xml.product)
        except IntegrityError:
            return HttpResponse(error_xml('Product already exist.'),
                    mimetype="application/xml")
        return response_xml(product)
        
    def do_PUT(self, id):
        product = Product.objects.get(id=id)
        update_model(product, self.xml.product)
        return response_xml(product)


class PersonController(Controller):
    def do_GET(self):
        people = Person.objects.all()
        return response_xml(people)
        
    def do_POST(self):
        person = Person()
        try:
            update_model(person, self.xml.person)
        except IntegrityError:
            return HttpResponse(error_xml('Person already exist.'),
                    mimetype="application/xml")
        return response_xml(person)
                        
    def do_PUT(self, id):
        person = Person.objects.get(id=id)
        update_model(person, self.xml.person)
        return response_xml(person)


class OrderController(Controller):
    def do_GET(self):
        orders = Order.objects.all()
        return response_xml(orders)

    def do_POST(self):
        order = Order()
        update_model(order, self.xml.order)
        return response_xml(order)
        
    def do_PUT(self, id):
        order = Order.objects.get(id=id)
        update_model(order, self.xml.order)
        return response_xml(order)

    def do_DELETE(self, id):
        order = Order.objects.get(id=id)
        order.delete()
        return response_xml(order)


class OrderItemController(Controller):
    def do_GET(self):
        order_items = OrderItem.objects.all()
        return response_xml(order_items)

    def do_POST(self):
        order_item = OrderItem()
        update_model(order_item, self.xml.order_item)
        return response_xml(order_item)

    def do_DELETE(self, id):
        order_item = OrderItem.objects.get(id=id)
        order_item.delete()
        return response_xml(order_item)


class BankAccountController(Controller):
    def do_GET(self):
        bank_accounts = BankAccount.objects.all()
        return response_xml(bank_accounts)


class PhoneNumberController(Controller):
    def do_GET(self):
        phone_numbers = PhoneNumber.objects.all()
        return response_xml(phone_numbers)


class PaymentController(Controller):
    def do_GET(self):
        payments = Payment.objects.all()
        return response_xml(payments)
        
    def do_POST(self):
        payment = Payment()
        update_model(payment, self.xml.payment)
        return response_xml(payment)
