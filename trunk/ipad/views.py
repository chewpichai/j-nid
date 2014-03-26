from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
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
    order = get_object_or_404(Order, id=id)
    product_types = ProductType.objects.filter(
                        products__is_sale=True).distinct()
    products = Product.objects.filter(is_sale=True)
    baskets = Basket.objects.filter(is_sale=True)
    return render(request, 'ipad/order-edit.html', locals())