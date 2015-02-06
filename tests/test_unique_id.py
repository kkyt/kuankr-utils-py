from kuankr_utils import log, debug, unique_id

def test_snowflake():
    s = unique_id.Snowflake()
    for i in range(100):
        x = s.next()
        b = "{0:b}".format(x)
        print x, b, len(b)
