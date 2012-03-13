from django.contrib import auth
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from j_nid.app.models import *
from j_nid.app.views import response_xml
import decimal
import datetime

def response_json(data):
    response = HttpResponse(mimetype='application/json')
    serializers.serialize('json', data, ensure_ascii=False, stream=response)
    return response

# =============================================================================

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return HttpResponse()
    return HttpResponseForbidden()

def get_producttypes(request):
    producttypes = ProductType.objects.filter(products__is_sale=True).distinct()
    return response_json(producttypes)

def get_products(request):
    products = Product.objects.filter(is_sale=True)
    return response_json(products)

def get_customers(requset):
    customers = Person.objects.filter(is_customer=True).order_by('name')
    return response_json(customers)

def get_baskets(request):
    baskets = Basket.objects.filter(is_sale=True)
    return response_json(baskets)

def create_order(request):
    obj =  simplejson.loads(request.raw_post_data)
    order = Order.objects.create(notation=obj['notation'],
                person_id=obj['person'], created=datetime.datetime.now())
    for item in obj['order_items']:
        if item['is_basket']:
            for i in xrange(int(item['unit'])):
                order.order_baskets.create(basket_id=item['product'],
                                           price_per_unit=item['price_per_unit'],
                                           is_deposit=item['is_deposit'])
        else:
            order.order_items.create(product_id=item['product'],
                                     price_per_unit=item['price_per_unit'],
                                     unit=item['unit'],
                                     cost_per_unit=item['cost_per_unit'])
    order.save()
    paid = decimal.Decimal(obj['paid'])
    if paid:
        created = order.created + datetime.timedelta(seconds=30)
        Payment.objects.create(person=order.person,
            amount=paid, created=created)
        for o in order.person.orders.extra(where=['paid <> total']).order_by('created'):
            if paid <= 0:
                break
            paid -= o.total - o.paid
            o.save()
    return HttpResponse(order.pk)
