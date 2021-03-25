import math

def is_prime(num):
    try:
        int(num)
    except ValueError:
        return "Not an integer!"
    lim = round(math.sqrt(num))
    for i in range(2, lim+1):
        if num % i == 0:
            return False
    return True
