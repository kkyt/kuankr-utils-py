from kuankr_utils.logstash import log

def test_simple():
    log.info('hello')
    log.info('hello', extra={'world': 'china'})

if __name__ == '__main__':
    test_simple()

