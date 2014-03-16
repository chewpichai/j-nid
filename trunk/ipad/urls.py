from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'ipad/login.html'}, name='ipad.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/ipad/'}, name='ipad.logout'),
)

urlpatterns += patterns('j_nid.ipad.views',
    url(r'^order/create/$', 'get_order_form', name='ipad.order_create'),
)
