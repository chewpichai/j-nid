from django.db import models, IntegrityError
from django.db.models.fields.related import RelatedField
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from j_nid.app.models import BankAccount, Order, Person, PhoneNumber, Product, ProductType
from p4x import P4X
from xml.parsers.expat import ExpatError

def get_banks(request):
    return render_to_response('app/bank_list.xml', {'banks': BankAccount.BANK_CHOICES},
                mimetype="application/xml")
    
def get_phonetypes(request):
    return render_to_response('app/phonetype_list.xml', {'phone_types': PhoneNumber.TYPE_CHOICES},
                mimetype="application/xml")

def update_model(model, xml):
    for field in model._meta.fields:
        try:
            name = field.name
            value = getattr(xml, field.name)[0].value
            if isinstance(field, models.BooleanField): value = int(value)
            elif isinstance(field, models.CharField): value = value or ''
            elif isinstance(field, models.TextField): value = value or ''
            elif issubclass(field.__class__, RelatedField): name = '%s_id' % field.name
            setattr(model, name, value)
        except TypeError: continue
    model.save()
    
def model_to_xml(model):
    xml = ['<%s>' % model._meta.verbose_name]
    for attr in model.__dict__:
        if not attr.startswith('_'):
            value = model.__dict__[attr]
            if value.__class__ == bool: value = int(value)
            xml.append('<%s>%s</%s>' % (attr, value, attr))
    xml.append('</%s>' % model._meta.verbose_name)
    return ''.join(xml)
            
def query_set_to_xml(query_set):
    xml = ['<?xml version="1.0" encoding="utf-8"?>']
    xml.append('<%s>' % query_set.model._meta.db_table)
    for model in query_set: xml.append(model_to_xml(model))
    xml.append('</%s>' % query_set.model._meta.db_table)
    return ''.join(xml)

class Controller(object):
    def __call__(self, request, **kwargs):
        self.request = request
        self.params = request.REQUEST
        method = request.method
        if request.raw_post_data:
            try:
                self.xml = P4X(self.request.raw_post_data)
                method =  self.xml.method[0].value
            except ExpatError: pass
        try: callback = getattr(self, 'do_%s' % method)
        except AttributeError: return HttpResponseNotFound()
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
        return HttpResponse(query_set_to_xml(product_types), mimetype='application/xml')
        
    def do_POST(self):
        product_type = ProductType()
        try:
            update_model(product_type, self.xml.product_type)
            return render_to_response('app/product_type_detail.xml', {'product_type': product_type},
                        mimetype="application/xml")
        except IntegrityError:
            return render_to_response('app/message.xml', {'message': 'Product type already exist.'},
                        mimetype="application/xml")
    
class ProductController(Controller):
    def do_GET(self):
        products = Product.objects.all()
        return HttpResponse(query_set_to_xml(products), mimetype='application/xml')
        
    def do_POST(self):
        product = Product()
        try:
            update_model(product, self.xml.product)
            return render_to_response('app/product_detail.xml', {'product': product},
                        mimetype="application/xml")
        except IntegrityError:
            return render_to_response('app/message.xml', {'message': 'Product already exist.'},
                        mimetype="application/xml")
        
    def do_PUT(self, id):
        product = Product.objects.get(id=id)
        update_model(product, self.xml.product)
        return render_to_response('app/product_detail.xml', {'product': product},
                    mimetype="application/xml")

class PersonController(Controller):
    def do_GET(self):
        people = Person.objects.all()
        return HttpResponse(query_set_to_xml(people), mimetype='application/xml')
        
    def do_POST(self):
        person = Person()
        try:
            update_model(person, self.xml.person)
            if self.xml.person.phone_number:
                for phone_number in self.xml.person.phone_number:
                    person.phone_numbers.create(
                        number=phone_number.number[0].value,
                        type=phone_number.type[0].value
                    )
            if self.xml.person.bank_account:
                for bank_account in self.xml.person.bank_account:
                    person.bank_accounts.create(
                        number=bank_account.number[0].value,
                        bank=bank_account.bank[0].value
                    )
            return render_to_response('app/person_detail.xml', {'person': person},
                        mimetype="application/xml")
        except IntegrityError:
            return render_to_response('app/message.xml', {'message': 'Person already exist.'},
                        mimetype="application/xml")
                        
    def do_PUT(self, id):
        person = Person.objects.get(id=id)
        update_model(person, self.xml.person)
        person.bank_accounts.all().delete()
        person.phone_numbers.all().delete()
        if self.xml.person.phone_number:
            for phone_number in self.xml.person.phone_number:
                person.phone_numbers.create(
                    number=phone_number.number[0].value,
                    type=phone_number.type[0].value
                )
        if self.xml.person.bank_account:
            for bank_account in self.xml.person.bank_account:
                person.bank_accounts.create(
                    number=bank_account.number[0].value,
                    bank=bank_account.bank[0].value
                )
        return render_to_response('app/person_detail.xml', {'person': person},
                    mimetype="application/xml")
                        
class OrderController(Controller):
    def do_POST(self):
        order = Order()
        update_model(order, self.xml.order)
        for item in self.xml.order.order_item:
            order.order_items.create(
                product=Product.objects.get(id=item.product[0].value),
                price_per_unit=item.price_per_unit[0].value,
                amount=item.amount[0].value
            )
        return render_to_response('app/order_detail.xml', {'order': order},
                        mimetype="application/xml")
                        
class BankAccountController(Controller):
    def do_GET(self):
        bank_accounts = BankAccount.objects.all()
        return HttpResponse(query_set_to_xml(bank_accounts), mimetype='application/xml')
        
class PhoneNumberController(Controller):
    def do_GET(self):
        phone_numbers = PhoneNumber.objects.all()
        return HttpResponse(query_set_to_xml(phone_numbers), mimetype='application/xml')
