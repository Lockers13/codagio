import math

def is_prime(inputs):
    for num in inputs:
        try:
            int(num)
        except ValueError:
            print("{0} : {1}".format(num, "Not an integer!"))
            continue
        lim = round(math.sqrt(num))
        is_prime = True
        for i in range(2, lim+1):
            if num % i == 0:
                is_prime = False
        print("{0} : {1}".format(num, is_prime))
