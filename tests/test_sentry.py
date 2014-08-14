from kuankr_utils import log, debug, sentry


def test_sentry():
    sentry.ensure_client()
    try:
        1/0
    except:
        log.exception('test error')

