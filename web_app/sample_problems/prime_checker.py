import json
import sys
import math

def is_prime(num):
    lim = round(math.sqrt(num))
    for i in range(2, lim+1):
        if num % i == 0:
            return False
    return True
    
def prep_input():
    try:
        return json.loads(sys.argv[1])
    except IndexError:
        print("Error: please make sure correct input has been provided")
        sys.exit(1)

def main():
    input_list = prep_input()
    for inp in input_list:
        print("{0} {1}".format(inp, is_prime(inp)))

main()