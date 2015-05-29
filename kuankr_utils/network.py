
import random
import struct
import netifaces

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
        ifname = ['eth0', 'wlan0', 'en0']
        ifname += netifaces.interfaces()

    if isinstance(ifname, basestring):
        s = netifaces.ifaddresses(ifname)
        return s[netifaces.AF_INET][0]['addr']
    else:
        for s in ifname:
            try:
                ip = get_ip_address(s)
                return ip
            except:
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

