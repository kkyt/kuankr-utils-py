from click import command, option, argument, group, echo, File, Path

import yaml

from . import json
from .api_client import ApiClient

def run_api(method, args, file=None, data=None):
    service, resource, link = method.split('.')
    api = ApiClient(service).api
    r = getattr(api, resource)
    m = getattr(r, link)

    body = {}
    if data:
        body = yaml.load(data)
    elif file:
        f = open(file, 'r')
        body = yaml.load(f.read())
        f.close()
    r = m(*args, **body)
    echo(json.dumps(r, pretty=True))

@group()
def kr():
    pass

@kr.command(help='METHOD: service.resource.link eg: kuankr_auth.user.info')
@option('-d', '--data')
@option('-f', '--file', type=Path(exists=True))
@argument('method')
@argument('args', nargs=-1)
def run(method, args, file=None, data=None):
    return run_api(method, args, file, data)

def main():    
    kr()

