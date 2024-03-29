from django.conf.urls import *


urlpatterns = patterns('j_nid.api.views',
    url(r'^login/$', 'login', name='api-login'),
    url(r'^producttypes/$', 'get_producttypes', name='api-get-producttype-list'),
    url(r'^products/$', 'get_products', name='api-get-product-list'),
    url(r'^products/(?P<id>\d+)/$', 'get_product', name='api-get-product'),
    url(r'^customers/$', 'get_customers', name='api-get-customer-list'),
    url(r'^baskets/$', 'get_baskets', name='api-get-basket-list'),
    url(r'^orders/create/$', 'create_order', name='api-create-order'),
    url(r'^orders/(?P<id>\d+)/edit/$', 'edit_order', name='api-edit-order'),
    url(r'^print/$', 'do_print', name='api-print'),
)
