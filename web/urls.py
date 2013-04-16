from django.conf.urls import *
from django.views.generic import RedirectView


urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='daily-sales-report'), name='web.index'),
)


urlpatterns += patterns('j_nid.web.views',
    url(r'^customer-report/$', 'get_customer_report', name='web.customer_report'),
    url(r'^daily-sales-report/$', 'get_daily_sales_report', name='web.daily_sales_report'),
    url(r'^daily-transaction-report/$', 'get_daily_transaction_report', name='web.daily_transaction_report'),
    url(r'^monthly-sales-report/$', 'get_monthly_sales_report', name='web.monthly_sales_report'),
    url(r'^payment-report/$', 'get_payment_report', name='web.payment_report'),
    url(r'^order/(?P<id>\d+)/$', 'get_order', name='web.order'),
    url(r'^payment/(?P<id>\d+)/$', 'get_payment', name='web.payment'),
)
