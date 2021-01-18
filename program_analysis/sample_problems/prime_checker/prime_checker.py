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
        with open(sys.argv[1], 'r') as f:
            contents = json.loads(f.read())
        return contents[int(sys.argv[2])]
    except (IndexError, FileNotFoundError):
        print("Error: please make sure correct input has been provided")
        sys.exit(1)

def main():
    num_list = prep_input()
    for num in num_list:
        print("{0} {1}".format(num, is_prime(num)))

main()