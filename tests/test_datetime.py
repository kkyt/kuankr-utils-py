from kuankr_utils.date_time import *

def test_simple():
    print datetime.now().isoformat()
    print utcnow().isoformat()
    print now()
    print now().isoformat()
    print to_str(now())

