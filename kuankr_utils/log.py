import logging
import os
import sys
import traceback
import inspect

from colorama import Fore, Back, Style
#from colorlog import ColoredFormatter

from sys import version_info
from logging import Formatter
from colorlog.escape_codes import escape_codes

"""
http://www.python.org/dev/peps/pep-0008/
_single_leading_underscore: weak "internal use" indicator. E.g. from M import * does not import objects whose name starts with an underscore.
"""

__all__ = """
    info error warn debug debug2 debug3
    info_ error_ warn_ debug_
""".split()

LOG_MSG_MAX_LEN = 1024

# The default colors to use for the debug levels
default_log_colors =  {
	'DEBUG':    'white',
	'INFO':     'green',
	'WARNING':  'yellow',
	'ERROR':    'red',
	'CRITICAL': 'bold_red',
}

def str_abbr(s, maxlen=128, concat='...'):
    if not isinstance(s, basestring):
        s = str(s)
    if len(s)>maxlen:
        n = maxlen/2
        return s[:n] + concat + s[-n:]
    else:
        return s

class ColoredFormatter (Formatter):
    """    A formatter that allows colors to be placed in the format string, intended to help in creating prettier, more readable logging output. """

    def __init__ (self, format, datefmt=None, log_colors=default_log_colors, reset=True, style='%'):
        """
        :Parameters:
        - format (str): The format string to use
        - datefmt (str): A format string for the date
        - log_colors (dict): A mapping of log level names to color names
        - reset (bool): Implictly appends a reset code to all records unless set to False
        - style ('%' or '{' or '$'): The format style to use. No meaning prior to Python 3.2.
        
        The ``format``, ``datefmt`` and ``style`` args are passed on to the Formatter constructor.
        """
        if version_info > (3, 2):
            super(ColoredFormatter, self).__init__(format, datefmt, style=style)
        elif version_info > (2, 7):
            super(ColoredFormatter, self).__init__(format, datefmt)
        else:
            Formatter.__init__(self, format, datefmt)
        self.log_colors = log_colors
        self.reset = reset

    def format (self, record):
        # Add the color codes to the record
        record.__dict__.update(escape_codes)

        # If we recognise the level name,
        # add the levels color as `log_color`
        if record.levelname in self.log_colors:
            color = self.log_colors[record.levelname]
            record.log_color = escape_codes[color]
        else:
            record.log_color = ""

        record.__dict__['abbr_levelname'] = record.levelname[0]
        record.__dict__['pathname2'] = '.'.join(record.pathname.split('/')[-2:]).rstrip('.py')

        # Format the message
        if version_info > (2, 7):
            message = super(ColoredFormatter, self).format(record)
        else:
            message = Formatter.format(self, record)

        # Add a reset code to the end of the message (if it wasn't explicitly added in format str)
        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        if len(message)>LOG_MSG_MAX_LEN:
            message = str_abbr(message, LOG_MSG_MAX_LEN)
        return message

colored_formatter = ColoredFormatter(
        #"%(asctime)s %(levelname)5s %(filename)64s%(lineno)4d %(log_color)s%(message)s%(reset)s",
        "%(green)s%(asctime)s %(white)s%(pathname2)24s%(cyan)s%(lineno)4d %(log_color)s[%(abbr_levelname)s] %(message)s%(reset)s",
        datefmt="%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'bold_green',
            'INFO':     'bold_cyan',
            'WARNING':  'bold_yellow',
            'ERROR':    'bold_red',
            'CRITICAL': 'bold_red',
        }
)


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(colored_formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

info = logger.info
error = logger.error
warn = logger.warn
debug = logger.debug
debug2 = logger.warn
debug3 = logger.error

def _empty(*args, **kwargs): pass

debug_ = info_ = warn_ = error_ = _empty

