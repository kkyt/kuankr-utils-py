from click import command, option, argument, group, echo, File, Path

import yaml

from . import log, debug, json, cli
from .api_client import ApiClient

def run_api(method, args, file=None, data=None, doc=False):
    a = method.split('.')
    service = resource = link = None

    if len(a)>=1:
        service = a[0]
    if len(a)>=2:
        resource = a[1]
    if len(a)>=3:
        link = a[2]

    if not a or len(a)>3:
        echo('method format should be service.resource.link or service.resource or service')
        return

    client = ApiClient(service)
    resources = sorted(client.api._resources.keys())

    links = {}
    full_links = {}
    for r in resources:
        links[r] = sorted(client.api._resources[r]._links.keys())
        d = {}
        for k,v in client.api._resources[r]._links.items():
            s = dict(v.schema)
            if 'href' in s:
                s['href'] = s['href'].replace('%23', '#').replace('%2F', '/')
            d[k] = s
        full_links[r] = d

    if not resource:
        r = links
    elif not link:
        r = full_links[resource]
    else:
        if doc:
            r = full_links[resource][link]
        else:
            r = getattr(client.api, resource)
            m = getattr(r, link)

            body = {}
            if data:
                body = yaml.load(data)
            elif file:
                f = open(file, 'r')
                body = yaml.load(f.read())
                f.close()
            r = m(*args, **body)

    cli.echo_json(r)

@group()
def kr():
    pass

@kr.command(help='METHOD: service.resource.link eg: kuankr_auth.user.info')
@option('-d', '--data')
@option('-f', '--file', type=Path(exists=True))
@option('--doc', is_flag=True)
@argument('method')
@argument('args', nargs=-1)
def run(method, args, file=None, doc=False, data=None):
    return run_api(method, args, file, data, doc=doc)

def main():    
    kr()

