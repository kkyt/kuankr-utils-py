from kuankr_utils.dicts import *

def test_recursive_merge_with_list():
    a = [{'a': 3}, {'b': [1,2,3]}]
    b = [{'b': 5}, {'c': 6, 'b': ['a']}, []]
    c = recursive_merge_with_list(a, b)
    assert c == [{'a': 3, 'b': 5}, {'c': 6, 'b': ['a', 2, 3]}, []]
