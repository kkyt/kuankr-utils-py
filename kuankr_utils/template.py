import os
import yaml
import jinja2
import string

from . import debug, date_time

def render_jinja2(t, params=None):
    t = jinja2.Template(t)
    ps = {
        '_env': dict(os.environ),
        '_now': date_time.to_str(date_time.now())
    }
    if params:
        ps.update(params)
    return t.render(**ps)


def render_simple(t, params=None, safe=True):
    if not t:
        return t
    if params is None:
        params = dict(os.environ)
        x = date_time.now_str()
        params['DATE'] = x[:date_time.DATE_LEN]
        params['TIME'] = x[:date_time.DATETIME_LEN]
    t = string.Template(t)
    if safe:
        return t.safe_substitute(params)
    else:
        return t.substitute(params)

