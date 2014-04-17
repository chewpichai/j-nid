from django.conf.urls import *
from j_nid.app import views

urlpatterns = patterns('',
    url(r'^banks/$', views.BankController()),
    url(r'^bankaccounts/$', views.BankAccountController()),
    url(r'^bankaccounts/(?P<id>\d+)/$', views.BankAccountController()),
    url(r'^baskets/$', views.BasketController()),
    url(r'^baskets/(?P<id>\d+)/$', views.BasketController()),
    url(r'^basketorders/$', views.BasketOrderController()),
    url(r'^orders/$', views.OrderController()),
    url(r'^orders/(?P<id>\d+)/$', views.OrderController()),
    url(r'^orders/(?P<order_id>\d+)/baskets/$', views.BasketOrderController()),
    url(r'^orderitems/$', views.OrderItemController()),
    url(r'^orderitems/(?P<id>\d+)/$', views.OrderItemController()),
    url(r'^payments/$', views.PaymentController()),
    url(r'^payments/(?P<id>\d+)/$', views.PaymentController()),
    url(r'^payments/(?P<payment_id>\d+)/baskets/$', views.BasketOrderController()),
    url(r'^people/$', views.PersonController()),
    url(r'^people/summary/$', views.get_people_summary),
    url(r'^people/(?P<id>\d+)/$', views.PersonController()),
    url(r'^people/(?P<person_id>\d+)/payments/$', views.PaymentController()),
    url(r'^people/(?P<person_id>\d+)/baskets/$', views.BasketOrderController()),
    url(r'^people/(?P<person_id>\d+)/transactions/$', views.get_person_transactions),
    url(r'^phonenumbers/$', views.PhoneNumberController()),
    url(r'^phonenumbers/(?P<id>\d+)/$', views.PhoneNumberController()),
    url(r'^phonetypes/$', views.PhoneTypeController()),
    url(r'^products/$', views.ProductController()),
    url(r'^products/stats/$', views.get_products_stats),
    url(r'^products/stats/detail/$', views.get_products_stats_detail),
    url(r'^products/(?P<id>\d+)/$', views.ProductController()),
    url(r'^products/(?P<id>\d+)/stats/$', views.get_product_stats),
    url(r'^producttypes/$', views.ProductTypeController()),
    url(r'^producttypes/(?P<id>\d+)/$', views.ProductTypeController()),
    url(r'^reports/$', views.get_year_list),
    url(r'^reports/(?P<year>\d+)/$', views.get_month_list),
    url(r'^reports/(?P<year>\d+)/(?P<month>\d+)/$', views.get_monthly_report),
    url(r'^sessions/$', views.SessionController()),
	url(r'^supplies/$', views.SupplyController()),
    url(r'^supplies/(?P<id>\d+)/$', views.SupplyController()),
    url(r'^supplyitems/$', views.SupplyItemController()),
    url(r'^supplyitems/(?P<id>\d+)/$', views.SupplyItemController()),
    url(r'^transactions/$', views.get_transactions),
)