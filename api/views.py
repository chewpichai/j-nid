from django.contrib import auth
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template import Context, Template
from django.utils import simplejson as json
from j_nid.app.models import *
from j_nid.app.views import response_xml
import decimal
import datetime
import os
import tempfile
import subprocess


def response_json(data):
    response = HttpResponse(mimetype='application/json')
    serializers.serialize('json', data, ensure_ascii=False, stream=response)
    return response


def format_number(num):
    t = Template("{% load humanize %}{{ num|floatformat|intcomma }}")
    return t.render(Context({'num': num}))

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


def get_product(request, id):
    product = get_object_or_404(Product, pk=id)

    if request.method == 'POST':
        product.price_per_unit = decimal.Decimal(request.POST.get('price'))
        product.cost_per_unit = decimal.Decimal(request.POST.get('cost'))
        product.save()
        data = {'pk': product.pk, 'price': product.price_per_unit,
                'formated_price': format_number(product.price_per_unit),
                'cost': product.cost_per_unit,
                'formated_cost': format_number(product.cost_per_unit)}
        return HttpResponse(json.dumps(data), content_type='application/json')


def get_customers(requset):
    customers = Person.objects.filter(is_customer=True).order_by('name')
    return response_json(customers)


def get_baskets(request):
    baskets = Basket.objects.filter(is_sale=True)
    return response_json(baskets)


def create_order(request):
    obj = json.loads(request.body, parse_float=decimal.Decimal)
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


def edit_order(request, id):
    obj = json.loads(request.body, parse_float=decimal.Decimal)
    order = get_object_or_404(Order, pk=id)
    before_total = order.total
    import base64
    order.notation = base64.b64decode(obj['notation'])
    
    order.order_baskets.all().delete()

    for item in obj['order_items']:
        if item.get('id') and not item['is_basket']:
            order_item = order.order_items.get(id=item['id'])
            order_item.price_per_unit = item['price_per_unit']
            order_item.unit = item['unit']
            order_item.is_deleted = item['is_deleted']
            order_item.save()
            continue

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

    after_total = order.total
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

    return HttpResponse(order.pk)


def do_print(request):
    url = request.GET.get('url')
    cmd_path = os.path.join(os.path.dirname(__file__), 'cmd', 'print.js')
    out_path = os.path.join(tempfile.gettempdir(), 'cmd', 'print.pdf')
    subprocess.Popen('C:\phantomjs\phantomjs.exe "%s" "%s" "%s"' % (cmd_path, url, out_path), shell=True).wait()
    subprocess.Popen('"C:\Program Files (x86)\Adobe\Reader 11.0\Reader\AcroRd32.exe" /T "%s"' % out_path, shell=True)
    return HttpResponse()
