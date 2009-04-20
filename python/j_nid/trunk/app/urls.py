from django.conf.urls.defaults import *
from j_nid.app import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^banknames/$', views.get_banks),
    (r'^bankaccounts/$', views.BankAccountController()),
    (r'^orders/$', views.OrderController()),
    (r'^orders/(?P<id>\d+)/$', views.OrderController()),
    (r'^orderitems/$', views.OrderItemController()),
    (r'^orderitems/(?P<id>\d+)/$', views.OrderItemController()),
    (r'^payments/$', views.PaymentController()),
    (r'^people/$', views.PersonController()),
    (r'^people/(?P<id>\d+)/$', views.PersonController()),
    (r'^phonenumbers/$', views.PhoneNumberController()),
    (r'^phonetypes/$', views.get_phonetypes),
    (r'^producttypes/$', views.ProductTypeController()),
    (r'^producttypes/(?P<id>\d+)/$', views.ProductTypeController()),
    (r'^products/$', views.ProductController()),
    (r'^products/(?P<id>\d+)/$', views.ProductController()),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
