from . import json

import click

def echo_json(r):    
    click.echo(json.dumps(r, pretty=True))

def echo_json_stream(stream):    
    for r in stream:
        click.echo(json.dumps(r)+'\n')

