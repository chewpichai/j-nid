from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from j_nid.app.models import *


@login_required(login_url='/ipad/')
def get_order_form(request):
	product_types = ProductType.objects.filter(
						products__is_sale=True).distinct()
	products = Product.objects.filter(is_sale=True)
	baskets = Basket.objects.filter(is_sale=True)
	customers = Person.objects.filter(is_customer=True)
	return render(request, 'ipad/order-form.html', locals())
