import commandr

from pyutils import log, debug

@commandr.command
def ping():
    return 'pong'

def main():
    try:
        commandr.Run()
    except:
        print debug.pretty_traceback()


