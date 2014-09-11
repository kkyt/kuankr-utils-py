import os
import yaml
import jinja2

from . import date_time

def render_jinja2(t, params=None):
    t = jinja2.Template(t)
    ps = {
        '_env': dict(os.environ),
        '_now': date_time.to_str(date_time.now())
    }
    if params:
        ps.update(params)
    return t.render(**ps)


