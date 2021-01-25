from mylibrary import dummy

def test_func():
    result = dummy.dummy_func()
    assert result == 1
    
def test_subtract():
    result = dummy.subtract(5,3)
    assert result == 2
