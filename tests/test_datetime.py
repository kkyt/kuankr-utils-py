from kuankr_utils.datetime import *

def test_simple():
    print datetime.now().isoformat()
    print utcnow().isoformat()
    print now()
    print now().isoformat()
    print to_str(now())

