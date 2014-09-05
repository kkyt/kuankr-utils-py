
from click import secho, echo

from . import json

def echo_json(a, **kwargs):
    secho(json.dumps(a, pretty=True), **kwargs)
    
