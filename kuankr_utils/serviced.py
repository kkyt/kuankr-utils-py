from __future__ import absolute_import

import os
import sys
from collections import defaultdict

from kuankr_utils import log, debug, network, json

class ServiceD(object):
    def __init__(self, **options):
        self.options = options
        self.services = defaultdict(list)
        self.set_options(**options)
        self._shutdown = False
        self._shutdown_handler_installed = False

    def normalize_uri(self, uri):
        local_ip = network.get_ip_address()
        old_uri = uri.strip()
        uri = uri.replace('127.0.0.1', local_ip)
        if uri != old_uri:
            log.info('local ip: %s' % local_ip)
            log.info('ServiceD.normalize_uri: %s -> %s' % (old_uri, uri))
        return uri

    def set_options(self):
        pass

    def setup(self):
        log.info('ServiceD.setup')
        log.info(self.list())

    def shutdown(self):
        log.info('ServiceD.shutdown')
        if self._shutdown:
            return
        for s in self.services:
            for uri in self.services[s]:
                self.unregister(s, uri)
        self._shutdown = True

    def shutdown_handler(self, *args):
        log.info('ServiceD.shutdown_handler: %s' % str(args))
        self.shutdown()
        raise Exception("shutdown")

    def install_shutdown_handler(self):
        import gevent
        from signal import SIGTERM, SIGINT, SIGABRT, signal

        if _sd is not None:
            for s in [SIGINT, SIGTERM, SIGABRT]:
                gevent.signal(s, _sd.shutdown_handler)

    def _register(self, service, uri):
        raise NotImplementedError()

    def register(self, service, uri):
        log.info('ServiceD.register: %s %s' % (service, uri))

        if not self._shutdown_handler_installed:
            self._shutdown_handler_installed = True
            self.install_shutdown_handler()

        uri = self.normalize_uri(uri)
        self.services[service].append(uri)
        return self._register(service, uri)

    def _unregister(self, service, uri):
        raise NotImplementedError()

    def unregister(self, service, uri):
        log.info('ServiceD.unregister: %s %s' % (service, uri))
        uri = self.normalize_uri(uri)
        self.services[service].remove(uri)
        return self._unregister(service, uri)

    def delete(self, service=None):
        log.info('ServiceD.delete: %s' % service)
        if service is None:
            self.services.clear()
        elif service in self.services:
            del self.services[service]
        return self._delete(service)

    def _lookup(self, service):
        raise NotImplementedError()

    def lookup(self, service, wait=False, all=False):
        url = os.environ.get('%s_URI' % service.upper())
        if url is None:
            url = self._lookup(service, wait=wait, all=all)
        else:
            log.info('ServiceD.lookup from env: %s %s' % (service, url))
            if all:
                url = [url]
        return url

    def list(self):
        raise NotImplementedError()

class RedisServiceD(ServiceD):
    #NOTE: set multi = False to ease debug
    def set_options(self, uri=None, multi=None):
        import redis

        if uri is None:
            uri = os.environ.get('KUANKR_SERVICED', 'redis://127.0.0.1:6379/1')
        if multi is None:
            multi = os.environ.get('KUANKR_SERVICED_MULTI')!='0'
        log.info('RedisServiceD.init: %s, multi: %s' % (uri, multi))

        uri_list = uri.split(',')
        self.rs = [redis.StrictRedis.from_url(u) for u in uri_list]
        self.r = self.rs[0]
        self.multi = multi

        self.key = 'KrSD:'

    def _register(self, service, uri):
        k = self.key
        if not self.multi:
            self._delete(service)
        self.r.sadd(k + service, uri)
        self.r.sadd(k, service)
    
    def _unregister(self, service, uri):
        k = self.key
        if not self.multi:
            self._delete(service)
        else:
            self.r.srem(k + service, uri)

        if self.r.scard(k + service)==0:
            self.r.srem(k, service)
        
    def _delete(self, service=None):
        if service is None:
            for s in self.list():
                self.delete(s)
        else:
            self.r.delete(self.key + service)
            self.r.srem(self.key, service)

    def list(self):
        r = {}
        for s in self.r.smembers(self.key):
            r[s] = self.lookup(s, wait=False, all=True)
        return r

    def _lookup_redis(self, r, service, all):
        k = self.key + service
        if all:
            return list(r.smembers(k))
        else:
            return r.srandmember(k)

    def _lookup(self, service, wait=True, all=False):
        if wait:
            import gevent
            s = 0.1
            while True:
                x = self._lookup(service, wait=False, all=all)
                if x:
                    return x
                else:
                    log.info('wait for service: %s, sleep %s' % (service, s))
                    gevent.sleep(s)
                    s *= 2
        else:
            for r in self.rs:
                x = self._lookup_redis(r, service, all)
                if x:
                    return x


_sd = None

def get_serviced(**kwargs):
    global _sd
    if _sd is None:
        try:
            _sd = RedisServiceD(**kwargs)
        except Exception as e:
            log.info('RedisServiceD error, use default: %s' % e)
            _sd = ServiceD()
        _sd.setup()

    return _sd

def register_cli(cli):
    from click import echo, option, argument, confirm, pass_context
    from kuankr_utils.click_utils import echo_json

    sd = get_serviced()

    @cli.command('list')
    @pass_context
    def list_service(ctx):
        echo_json(sd.list())
        
    @cli.command('lookup')
    @argument('name')
    @pass_context
    def list_service(ctx, name):
        echo_json(sd.lookup(name))

    @cli.command('delete')
    @argument('name')
    @pass_context
    def list_service(ctx, name):
        sd.delete(name)

    @cli.command('register')
    @argument('name')
    @argument('uri')
    @pass_context
    def list_service(ctx, name, uri):
        sd.register(name, uri)

    @cli.command('clear')
    @pass_context
    def list_service(ctx):
        sd.delete()

'''
import etcd
class EtcdServiceD(ServiceD):
    #TODO
    def set_options(self, uri):
        if uri is None:
            uri = os.environ.get('KUANKR_SERVICED', 'etcd://127.0.0.1:4001')
        self.etcd = etcd.Client(host=host, port=port)
'''

