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
        with open(sys.argv[1], 'r') as f:
            contents = json.loads(f.read())
        return contents[int(sys.argv[2])]
    except (IndexError, FileNotFoundError):
        print("Error: please make sure correct input has been provided")
        sys.exit(1)

def main():
    string_list = prep_input()
    for rot_string in string_list:
        print("{0}".format(rot13(rot_string)))

main()