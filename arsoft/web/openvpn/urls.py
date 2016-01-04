from django.conf.urls import patterns, include, url
from django.conf import settings
from arsoft.web.utils import django_debug_urls

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'arsoft.web.openvpn.views.home', name='home'),
    url(r'^log/(?P<name>\w+)$', 'arsoft.web.openvpn.views.log', name='log'),
    url(r'^action/(?P<name>\w+)$', 'arsoft.web.openvpn.views.action', name='action'),
#    url(r'^%s$' % settings.BASE_URL, 'arsoft.web.openvpn.views.home', name='home'),
#    url(r'^%s/changepw$' % settings.BASE_URL, 'arsoft.web.openvpn.views.changepw', name='changepw'),
    # url(r'^arsoft.web.openvpn/', include('arsoft.web.openvpn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^debug/', include(django_debug_urls())),
)
