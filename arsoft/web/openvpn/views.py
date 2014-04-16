from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
import arsoft.openvpn

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):

    selected_vpns = ['myhome']
    _config = arsoft.openvpn.Config()
    _systemconfig = arsoft.openvpn.SystemConfig()
    all_vpn_names = _config.names
    if len(selected_vpns) == 0:
        selected_vpns = all_vpn_names

    class ConfigItem(object):
        def __init__(self, name, config_file, is_running, status_file, autostart=False):
            self.name = name
            self.config_file = config_file
            self.is_running = is_running
            self.status_file = status_file
            self.autostart = autostart

    config_list = []

    for vpnname in selected_vpns:
        config_file = arsoft.openvpn.ConfigFile(config_name=vpnname)
        is_running = _config.is_running(vpnname)
        autostart = True if vpnname in _systemconfig.autostart else False
        status_file = arsoft.openvpn.StatusFile(config_file=config_file)
        config_list.append( ConfigItem(vpnname, config_file=config_file, is_running=is_running, status_file=status_file, autostart=autostart) )

    title = 'OpenVPN status'

    t = loader.get_template('home.html')
    c = RequestContext( request, { 
        'config_list':config_list,
        'title':title
        })
    return HttpResponse(t.render(c))

