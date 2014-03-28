from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import simplejson as json
from j_nid.app.models import *
from j_nid.ipad.forms import *


@login_required(login_url='/ipad/')
def create_order(request):
    product_types = ProductType.objects.filter(
                        products__is_sale=True).distinct()
    products = Product.objects.filter(is_sale=True)
    baskets = Basket.objects.filter(is_sale=True)
    customers = Person.objects.filter(is_customer=True)
    return render(request, 'ipad/order-create.html', locals())


@login_required(login_url='/ipad/')
def search_order(request):
    customers = Person.objects.filter(is_customer=True)
    return render(request, 'ipad/order-search.html', locals())


@login_required(login_url='/ipad/')
def list_order(request):
    form = OrderSearchForm(request.GET)

    if form.is_valid():
        orders = form.get_orders()

    return render(request, 'ipad/order-list.html', locals())


@login_required(login_url='/ipad/')
def edit_order(request, id):
    request.session['order_list_url'] = request.META.get('HTTP_REFERER')
    order = get_object_or_404(Order, id=id)
    product_types = ProductType.objects.filter(
                        products__is_sale=True).distinct()
    products = Product.objects.filter(is_sale=True)
    baskets = Basket.objects.filter(is_sale=True)
    return render(request, 'ipad/order-edit.html', locals())

@login_required(login_url='/ipad/')
def delete_order(request, id):
    if request.method != 'POST': return HttpResponseForbidden()

    order = Order.objects.get(id=id)
    person = order.person
    amount = order.paid
    order.delete()
    
    for o in person.orders.extra(where=['paid <> total']).order_by('created'):
        if amount <= 0: break
        amount -= order.total - order.paid
        o.save()

    data = {'url': request.session['order_list_url'] or reverse('ipad.order_search'),
            'status': 'success'}
    return HttpResponse(json.dumps(data), content_type='application/json')