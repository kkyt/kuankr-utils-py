#coding:utf8

from kuankr_utils import csv

def test_csv():
    a = [1, 'ab""c', 3.2]
    assert csv.dumps(a) == '1,"ab""""c",3.2\r\n'

    a = [1, u'如\n果', 3.2]
    s = csv.dumps(a)
    assert s == '1,"如\n果",3.2\r\n'

    b = csv.loads(s)
    assert b==['1', '如\n果', '3.2']

    a = { 'a':1, 'b': 2}
    s = csv.dumps(a, headers=['b','a'])
    assert s=='2,1\r\n'
