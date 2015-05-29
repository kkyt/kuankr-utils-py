
from kuankr_utils.network import get_ip_address

def test_get_ip():
    ip = get_ip_address()
    print ip
    assert (ip is not None)

