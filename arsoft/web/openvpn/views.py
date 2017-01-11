from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
import arsoft.openvpn
from arsoft.timestamp import UTC, format_timedelta

import datetime

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ConfigCertItem(object):
    def __init__(self, cert_file_obj):
        self._cert_file_obj = cert_file_obj

        min_expire_cert = None
        if self._cert_file_obj.certificates:
            self._cert_obj = self._cert_file_obj.certificates[0]
            now = datetime.datetime.utcnow().replace(tzinfo=UTC)
            min_expire_in = datetime.timedelta(days=100*365)
            for cert in self._cert_file_obj.certificates:
                expire_in = cert.expire_date - now
                if expire_in < min_expire_in:
                    min_expire_in = expire_in
                    min_expire_cert = cert

        else:
            self._cert_obj = None
        self.filename = self._cert_file_obj.filename
        self.subject = 'CN=%s' % self._cert_obj.subject.commonName if self._cert_obj else None
        self.issuer = 'CN=%s' % self._cert_obj.issuer.commonName if self._cert_obj else None
        self.expire_date = min_expire_cert.expire_date if min_expire_cert else None
        self.issue_date = min_expire_cert.issue_date if min_expire_cert else None

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
            logger.error('%s routing_table=%s' % (self.name, self.status_file_obj.routing_table))
            for entry in self.status_file_obj.routing_table:
                self.routing_table.append(str(entry))

        self.certificate = ConfigCertItem(self.config_file.cert_file)
        self.ca_certificate = ConfigCertItem(self.config_file.ca_file)

        self.client_config_directory = self.config_file.client_config_directory if self.server else None
        self.connection_state_desc = self.status_file_obj.state.long_state if self.status_file_obj.state else None
        self.last_state_change = self.status_file_obj.state.timestamp if self.status_file_obj.state else None
        self.last_update = self.status_file_obj.last_update if self.status_file_obj else None
        self.connected_clients = []
        self.configured_clients = []
        if self.server:
            if self.status_file_obj.connected_clients:
                for (clientname, clientinfo) in self.status_file_obj.connected_clients.items():
                    self.connected_clients.append(str(clientinfo))
            if self.config_file.client_config_files:
                for (clientname, ccdfile) in self.config_file.client_config_files.items():
                    self.configured_clients.append(clientname)
        
        self.connection_state = 'unknown'
        self.running_state = 'unknown'
        self.last_update_state = 'unknown'
        if self.is_running and self.last_update:
            #now = datetime.datetime.utcnow().replace(tzinfo=UTC)
            now = datetime.datetime.now()
            time_since_last_update = now - self.last_update
            if time_since_last_update > datetime.timedelta(minutes=10):
                self.last_update_state = 'warning'
            else:
                self.last_update_state = 'ok'

        if self.autostart:
            if self.status_file_obj.state:
                if self.status_file_obj.state.is_down:
                    self.connection_state = 'critical'
                elif self.status_file_obj.state.is_connected:
                    self.connection_state = 'ok'
                else:
                    self.connection_state = 'warning'
            if self.is_running:
                self.running_state = 'ok'
            else:
                self.running_state = 'critical'
        else:
            if self.status_file_obj.state:
                if self.status_file_obj.state.is_down:
                    self.connection_state = 'ok'
                else:
                    self.connection_state = 'critical'
            if self.is_running:
                self.running_state = 'critical'
            else:
                self.running_state = 'ok'



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
    
    def logfile(self, vpnname):
        cfgfile = arsoft.openvpn.ConfigFile(config_name=vpnname)
        return cfgfile.logfile if cfgfile.logfile else cfgfile.logfile_append
    
    def config_file(self, vpnname):
        return arsoft.openvpn.ConfigFile(config_name=vpnname)
    
    def invoke_rc_d_openvpn(self, action, vpnname):
        invoke_args = ['/usr/bin/sudo', '/usr/bin/openvpn-admin', '--' + action, vpnname]
        (sts, stdoutdata, stderrdata) = arsoft.utils.runcmdAndGetData(invoke_args)
        return (sts, stdoutdata, stderrdata)

    def read_log(self, vpnname):
        invoke_args = ['/usr/bin/sudo', '/usr/bin/openvpn-admin', '--log', vpnname]
        (sts, stdoutdata, stderrdata) = arsoft.utils.runcmdAndGetData(invoke_args)
        return (sts, stdoutdata, stderrdata)

def home(request):

    hub = ConfigHub()
    title = 'OpenVPN status'

    logger.error('config_list=%s' % hub.list())

    t = loader.get_template('home.html')
    c = {
        'config_list':hub.list(),
        'title':title
        }
    return HttpResponse(t.render(c, request))

def action(request, name):
    action = request.POST.get("action", "")
    if not name:
        raise Http404("No VPN name specified.")
    if not action:
        raise Http404("No action for VPN %s specified." % name)

    hub = ConfigHub()
    configfile = hub.config_file(name)
    if configfile is None or not configfile.valid:
        raise Http404("Unable to get confgi for VPN %s" % name)
    
    if action == 'stop':
        (sts, stdoutdata, stderrdata) = hub.invoke_rc_d_openvpn('stop', name)
        ret = True if sts == 0 else False
        content = stdoutdata if ret else stderrdata
    elif action == 'start':
        (sts, stdoutdata, stderrdata) = hub.invoke_rc_d_openvpn('start', name)
        ret = True if sts == 0 else False
        content = stdoutdata if ret else stderrdata
    elif action == 'restart':
        (sts, stdoutdata, stderrdata) = hub.invoke_rc_d_openvpn('restart', name)
        ret = True if sts == 0 else False
        content = stdoutdata if ret else stderrdata
    else:
        ret = False

    if ret:
        content = 'OK'
    else:
        content = hub.config.last_error
    return HttpResponse(content, content_type='text/plain')

def log(request, name):
    hub = ConfigHub()
    
    (sts, stdoutdata, stderrdata) = hub.read_log(name)
        
    status = 200 if sts == 0 else 400
    content = stdoutdata if sts == 0 else stderrdata

    return HttpResponse(content, status=status, content_type='text/plain')

