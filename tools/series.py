import numpy as np

def fibonacci(n):
    try:
        if n < 0:
            raise ValueError('Negativity violates causality parameters')
        if n == 0:
            return None
        if n == 1:
            return 0
        if n == 2:
            return 1
        
        result = np.eye(2, dtype=object)
        base = np.array([[1, 1], [1, 0]], dtype=object)
        power = n - 1

        while power > 0:
            if power & 1:
                result = np.dot(result, base)
            base = np.dot(base, base)
            power >>= 1

        return int(result[0, 0])
    except Exception as e:
        print(f"Try again with a positive value or a smaller number")
        return None

def collatz(number):
    try:
        order = 0
        if number <= 0:
            raise ValueError('Only positive integers are allowed')
        while number != 1:
            if number%2 == 0:
                number //= 2
            else:
                number = 3 * number + 1
            order += 1
        return order
    except Exception:
        print(f"Try again with a positive value or a smaller number")
        return None

