from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import simplejson as json
from j_nid.app.models import *
from j_nid.ipad.forms import *
import datetime


@login_required(login_url='/ipad/')
def create_order(request):
    product_types = ProductType.objects.filter(
                        products__is_sale=True).distinct()
    products = Product.objects.filter(is_sale=True)
    baskets = Basket.objects.filter(is_sale=True)
    customers = Person.objects.filter(is_customer=True)
    page = 'order_create'
    return render(request, 'ipad/order-create.html', locals())


@login_required(login_url='/ipad/')
def list_order(request):
    data = request.GET or {'start_date': datetime.date.today().strftime('%d/%m/%Y')}
    form = OrderSearchForm(data)

    if form.is_valid():
        orders = form.get_orders()
    
    page = 'order_list'
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


def print_order(request, id):
    order = get_object_or_404(Order, id=id)
    items = list(order.order_items.all()) + list(order.get_deposit_baskets())
    item_pages = []
    nums_per_page = 13
    nums = len(items) / nums_per_page

    for i in range(nums + 1):
        page = items[i * nums_per_page:(i + 1) * nums_per_page]

        if page:
            remains = len(page) % nums_per_page

            if remains > 0:
                for i in range(remains, nums_per_page):
                    page.append({'name':'&nbsp;'})
            
            item_pages.append(page)
    
    return render(request, 'ipad/order-print.html', locals())