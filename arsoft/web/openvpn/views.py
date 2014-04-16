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
    all_vpn_names = self._config.names
    if len(selected_vpns) == 0:
        selected_vpns = all_vpn_names

    class ConfigItem(object):
        def __init__(self, name, status=None):
            self.name = name
            self.status = status

    config_list = []

    logging.error('ddd')

    for vpnname in selected_vpns:
        config_file = arsoft.openvpn.ConfigFile(config_name=vpnname)
        print(config_file)
        if not config_file.valid:
            config_list.append(ConfigItem(vpnname), 'invalid file')
        else:
            config_list.append(ConfigItem(vpnname), 'valid file')

    title = 'OpenVPN status'

    t = loader.get_template('home.html')
    c = RequestContext( request, { 
        'config_list':config_list,
        'title':title
        })
    return HttpResponse(t.render(c))

