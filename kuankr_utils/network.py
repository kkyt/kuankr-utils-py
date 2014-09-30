
import random
import socket
import fcntl
import struct

from . import log
 
def get_host_and_port(addr):
    if not addr:
        return '127.0.0.1', None

    #strip schema
    a = addr.split('://', 1)
    if len(a)>1:
        addr = a[1]

    #port is optional
    a = addr.split(':', 1)
    if len(a)>1:
        return a[0], int(a[1])
    else:
        return a[0], None

def get_ip_address(ifname=None):
    if ifname is None:
        ifname = ['eth0', 'wlan0', 'em0']

    if isinstance(ifname, basestring):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    else:
        for s in ifname:
            try:
                ip = get_ip_address(s)
                return ip
            except IOError, e:
                pass
        return None

#copy from pyzmq/zmq/sugar/socket.py
def bind_to_random_port(binder, addr, min_port=49152, max_port=65536, max_tries=100):
    """
    bind this socket to a random port in a range
    """
    for i in range(max_tries):
        try:
            port = random.randrange(min_port, max_port)
            binder('%s:%s' % (addr, port))
        except Exception, e:
            log.info('bind_to_random_port: %s' % e)
        else:
            return port
    raise Exception("Could not bind to random port.")

