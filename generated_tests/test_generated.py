import pytest
from src.tasks import calculate_discount, is_even, divide, read_source_code

def test_calculate_discount_normal():
    assert calculate_discount(100, 10) == 90.0
    assert calculate_discount(50, 25) == 37.5
    assert calculate_discount(1000, 50) == 500.0

def test_calculate_discount_edge():
    assert calculate_discount(100, 0) == 100.0
    assert calculate_discount(100, 100) == 0.0

def test_calculate_discount_error():
    with pytest.raises(ValueError):
        calculate_discount(-100, 10)
    with pytest.raises(ValueError):
        calculate_discount(100, -10)
    with pytest.raises(ValueError):
        calculate_discount(100, 110)

def test_is_even_normal():
    assert is_even(2) == True
    assert is_even(4) == True
    assert is_even(0) == True

def test_is_even_odd():
    assert is_even(1) == False
    assert is_even(3) == False
    assert is_even(-1) == False

def test_divide_normal():
    assert divide(10, 2) == 5.0
    assert divide(7, 2) == 3.5
    assert divide(1, 1) == 1.0

def test_divide_error():
    with pytest.raises(ValueError):
        divide(10, 0)

def test_read_source_code():
    # Create a dummy source file for testing
    with open("temp_source.py", "w") as f:
        f.write("def test_function():\n    pass\n")
    result = read_source_code("temp_source.py")
    assert result == "def test_function():\n    pass\n"

    with open("temp_source.py", "w") as f:
        f.write("")
    result = read_source_code("temp_source.py")
    assert result == ""