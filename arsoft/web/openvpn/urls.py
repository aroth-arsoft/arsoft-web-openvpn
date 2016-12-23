from django.conf.urls import include, url
from django.conf import settings
from arsoft.web.utils import django_debug_urls

import arsoft.web.openvpn.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^$', arsoft.web.openvpn.views.home, name='home'),
    url(r'^log/(?P<name>[\w\-]+)$', arsoft.web.openvpn.views.log, name='log'),
    url(r'^action/(?P<name>[\w\-]+)$', arsoft.web.openvpn.views.action, name='action'),

    url(r'^debug/', include(django_debug_urls())),
]
