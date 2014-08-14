import raven
import os

_sentry = None

def create_client():
    e = os.environ
    return raven.Client(
        dsn=e.get('SENTRY_DSN'),
        include_paths=e.get('SENTRY_INCLUDE_PATHS', '').split(','),
        exclude_paths=e.get('SENTRY_EXCLUDE_PATHS', '').split(','),
        servers=e.get('SENTRY_SERVERS'),
        name=e.get('SENTRY_NAME'),
        public_key=e.get('SENTRY_PUBLIC_KEY'),
        secret_key=e.get('SENTRY_SECRET_KEY'),
        project=e.get('SENTRY_PROJECT'),
        site=e.get('SENTRY_SITE_NAME'),
        processors=e.get('SENTRY_PROCESSORS'),
        string_max_length=e.get('SENTRY_MAX_LENGTH_STRING'),
        list_max_length=e.get('SENTRY_MAX_LENGTH_LIST'),
        extra={
        },
    )

def ensure_client():
    global _sentry
    if _sentry is None:
        set_client(create_client())
    return _sentry
    
def get_client():
    return _sentry

def set_client(c):
    global _sentry
    _sentry = c

def capture_exception():
    c = get_client()
    if c is not None:
        c.capture_exception()

