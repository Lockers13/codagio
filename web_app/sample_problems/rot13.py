import json
import sys

ABC_LOWER = "abcdefghijklmnopqrstuvwxyz"
ABC_UPPER = ABC_LOWER.upper()

def rot13(phrase):
    out_phrase = ""
    for char in phrase:
        if char.isupper():
            out_phrase += ABC_UPPER[(ABC_UPPER.find(char)+13)%26]
        else:
            out_phrase += ABC_LOWER[(ABC_LOWER.find(char)+13)%26]
    return out_phrase

def prep_input():
    try:
        return json.loads(sys.argv[1])
    except IndexError:
        print("Error: please make sure correct input has been provided")
        sys.exit(1)

def main():
    input_list = prep_input()
    for inp in input_list:
        print("{0} {1}".format(inp, rot13(inp)))

main()