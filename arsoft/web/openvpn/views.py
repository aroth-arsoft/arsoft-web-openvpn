from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
import arsoft.openvpn

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ConfigItem(object):
    def __init__(self, hub, config_file):
        self.hub = hub
        self.config_file = config_file
        self.name = self.config_file.name
        self.filename = self.config_file.filename
        self.is_running = self.hub.config.is_running(self.name)
        self.autostart = True if self.name in self.hub.systemconfig.autostart else False
        self.status_file_obj = arsoft.openvpn.StatusFile(config_file=self.config_file)
        self.status_version = self.config_file.status_version
        self.status_file = self.config_file.status_file
        self.logfile = self.config_file.logfile if self.config_file.logfile else self.config_file.logfile_append
        self.server = self.config_file.server
        self.routes = []
        for (network, netmask) in self.config_file.routes:
            self.routes.append( '%s/%s' % (network, netmask))
        self.routing_table = []
        if self.status_file_obj.routing_table:
            for entry in self.status_file_obj.routing_table:
                self.routing_table.append(str(entry))

        self.client_config_directory = self.config_file.client_config_directory if self.server else None
        self.connection_state = self.status_file_obj.state.long_state
        self.connected_clients = []
        self.configured_clients = []
        if self.server:
            if self.status_file_obj.connected_clients:
                for (clientname, clientinfo) in self.status_file_obj.connected_clients.iteritems():
                    self.connected_clients.append(str(clientinfo))
            if self.config_file.client_config_files:
                for (clientname, ccdfile) in self.config_file.client_config_files.iteritems():
                    self.configured_clients.append(clientname)



class ConfigHub(object):
    def __init__(self):
        self.config = arsoft.openvpn.Config()
        self.systemconfig = arsoft.openvpn.SystemConfig()

    def list(self, selected_vpns=[]):
        ret = []
        if not selected_vpns:
            selected_vpns = self.config.names

        logger.error('self.config.names=%s' % self.config.names)
        logger.error('selected_vpns=%s' % selected_vpns)
        for vpnname in selected_vpns:
            item = ConfigItem(self, arsoft.openvpn.ConfigFile(config_name=vpnname))
            ret.append(item)
        return ret

def home(request):

    hub = ConfigHub()
    title = 'OpenVPN status'

    logger.error('config_list=%s' % hub.list())

    t = loader.get_template('home.html')
    c = RequestContext( request, { 
        'config_list':hub.list(),
        'title':title
        })
    return HttpResponse(t.render(c))

