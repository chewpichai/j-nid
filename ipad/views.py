from django.shortcuts import render
from j_nid.app.models import *


def get_order_form(request):
	product_types = ProductType.objects.filter(
						products__is_sale=True).distinct()
	products = Product.objects.filter(is_sale=True)
	baskets = Basket.objects.filter(is_sale=True)
	customers = Person.objects.filter(is_customer=True)
	return render(request, 'ipad/order-form.html', locals())


def get_product_by_type(request):
	pass
