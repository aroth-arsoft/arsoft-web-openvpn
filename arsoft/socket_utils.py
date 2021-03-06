#!/usr/bin/python
# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;

import os
import sys
import socket

def create_unix_socket(path, mode, socktype=socket.SOCK_STREAM):
    # Make sure the socket does not already exist
    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise

    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socktype)

    # Bind the socket to the port
    sock.bind(path)

    # change permissions of the socket
    os.fchmod(sock.fileno(), mode)

    # Listen for incoming connections
    sock.listen(5)
    return sock

def close_unix_socket(sock):
    path = None
    try:
        path = sock.getsockname()
        sock.close()
    except socket.error as e:
        pass

    if path:
        # Make sure the socket does not already exist
        try:
            os.unlink(path)
        except OSError:
            if os.path.exists(path):
                raise

def connect_unix_socket(path, socktype=socket.SOCK_STREAM):
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socktype)

    # Connect the socket to the port where the server is listening
    sock.connect(path)
    return sock

def send_unix_socket_message(path, message, socktype=socket.SOCK_STREAM):
    try:
        sock = connect_unix_socket(path, socktype)
    except socket.error as e:
        sock = None
    ret = -1
    if sock is not None:
        try:
            sock.sendall(message)
            ret = len(message)
        finally:
            sock.close()
    return ret

def send_and_recv_unix_socket_message(path, message, socktype=socket.SOCK_STREAM, bufsize=4096):
    try:
        sock = connect_unix_socket(path, socktype)
    except socket.error as e:
        sock = None
    ret = None
    if sock is not None:
        try:
            sock.sendall(message)
            ret = sock.recv(bufsize)
        finally:
            sock.close()
    return ret

def sethostname(new_hostname):
    from utils import runcmdAndGetData
    (sts, stdoutdata, stderrdata) = runcmdAndGetData(['/bin/hostname', new_hostname])
    ret = True if sts == 0 else False
    return ret

def gethostname_tuple(fqdn=None):
    if fqdn is None:
        fqdn = socket.getfqdn().lower()
    else:
        fqdn = fqdn.lower()
    if '.' in fqdn:
        (hostname, domain) = fqdn.split('.', 1)
    else:
        hostname = fqdn
        domain = 'localdomain'
    return (fqdn, hostname, domain)

def gethostname(fqdn=True):
    ret = socket.getfqdn()
    if not fqdn:
        if '.' in ret:
            (ret, domain) = ret.split('.', 1)
    return ret

def getdomainname():
    fqdn = socket.getfqdn()
    if '.' in fqdn:
        (hostname, ret) = fqdn.split('.', 1)
    else:
        ret = 'localdomain'
    return ret

def getportbyname(servicename, protocolname=None):
    if protocolname is None:
        return socket.getservbyname(servicename)
    else:
        return socket.getservbyname(servicename, protocolname)
