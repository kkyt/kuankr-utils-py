import os
from time import sleep as time_sleep

try:
    from gevent import sleep as gevent_sleep
except:
    gevent_sleep = time_sleep

from . import log

if os.environ.get('SLEEP_DEBUG')=='1':
    sleep_debug = log.warn
else:
    sleep_debug = log.debug

def sync_sleep(s, msg=''):
    if s>0:
        sleep_debug("[sync sleep] %s secs: %s" % (s, msg))
    time_sleep(s)

def async_sleep(s, msg=''):
    if s>0:
        sleep_debug("[async sleep] %s secs: %s" % (s, msg))
    gevent_sleep(s)

sleep = async_sleep


