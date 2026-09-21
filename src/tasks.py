def calculate_discount(price, percentage):
    if price < 0:
        raise ValueError("price cannot be negative")
    if percentage < 0 or percentage > 100:
        raise ValueError("percentage must be between 0 and 100")
    return price * (1 - percentage / 100)


def is_even(number):
    return number % 2 == 0


def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b

