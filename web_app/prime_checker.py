import json
import sys

def is_prime(num):
    for i in range(2, num):
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
    input_list = prep_input()
    for inp in input_list:
        print("{0} {1}".format(inp, is_prime(inp)))

main()
