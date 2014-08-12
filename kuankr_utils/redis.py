from __future__ import absolute_import

import urllib
from urlparse import urlparse
import redis

#use redis.StrictRedis.from_url
'''
def create_client(uri):
    uri = urlparse(uri)

    username = uri.username
    if username:
        username = urllib.unquote(username)

    password = uri.password
    if password:
        password = urllib.unquote(password)

    db = 0
    if len(uri.path)>1:
        db = int(uri.path[1:])

    r = redis.StrictRedis(
        host=uri.hostname, 
        port=uri.port, 
        db=db,
        user=username,
        password=password
    )

    return r
'''

