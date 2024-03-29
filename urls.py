from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^api/', include('j_nid.api.urls')),
    (r'^j-nid/', include('j_nid.app.urls')),
    (r'^web/', include('j_nid.web.urls')),
    (r'^ipad/', include('j_nid.ipad.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
