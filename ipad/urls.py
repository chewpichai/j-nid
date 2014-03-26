from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'ipad/login.html'}, name='ipad.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/ipad/'}, name='ipad.logout'),
)

urlpatterns += patterns('j_nid.ipad.views',
    url(r'^order/$', 'list_order', name='ipad.order_list'),
    url(r'^order/(?P<id>\d+)/$', 'edit_order', name='ipad.order_edit'),
    url(r'^order/create/$', 'create_order', name='ipad.order_create'),
    url(r'^order/search/$', 'search_order', name='ipad.order_search'),
)
