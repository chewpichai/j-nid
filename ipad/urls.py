from django.conf.urls import *


urlpatterns = patterns('j_nid.ipad.views',
    url(r'^$', 'get_order_form', name='ipad.index'),
	url(r'^product-types/(?P<id>\d+)/products/$', 'get_product_by_type', name='ipad.product_by_type'),
)
