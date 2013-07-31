from django.conf.urls import *


urlpatterns = patterns('j_nid.web.views',
	url(r'^$', 'get_dashboard', name='web.index'),
    url(r'^customer/report/$', 'get_customer_report', name='web.customer_report'),
    url(r'^customer/search/$', 'get_customer_search', name='web.customer_search'),
    url(r'^customer/(?P<id>\d+)/$', 'get_customer_detail', name='web.customer_detail'),
    url(r'^daily-sales-report/$', 'get_daily_sales_report', name='web.daily_sales_report'),
    url(r'^daily-transaction-report/$', 'get_daily_transaction_report', name='web.daily_transaction_report'),
    url(r'^monthly-sales-report/$', 'get_monthly_sales_report', name='web.monthly_sales_report'),
    url(r'^payment-report/$', 'get_payment_report', name='web.payment_report'),
    url(r'^order/(?P<id>\d+)/$', 'get_order', name='web.order'),
    url(r'^payment/(?P<id>\d+)/$', 'get_payment', name='web.payment'),
)
