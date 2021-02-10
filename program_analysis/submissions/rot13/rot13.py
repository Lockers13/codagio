import sys
import json

def rot13(phrase):
    ascii_lower = (97, 122)
    ascii_upper = (65, 90)
    LEN_ALPHA = 26
    new_string = ""
    for char in phrase:
        ascii_num = ord(char)
        if ascii_num >= ascii_lower[0] and ascii_num <= ascii_lower[1]:
            if ((ascii_num - ascii_lower[0]) + 13) >= LEN_ALPHA:
                ascii_num = ascii_lower[0] + (((ascii_num - ascii_lower[0]) + 13) - LEN_ALPHA)
            else:
                ascii_num += 13
        elif ascii_num >= ascii_upper[0] and ascii_num <= ascii_upper[1]:
            if ((ascii_num - ascii_upper[0]) + 13) >= LEN_ALPHA:
                ascii_num = ascii_upper[0] + (((ascii_num - ascii_upper[0]) + 13) - LEN_ALPHA)
            else:
                ascii_num += 13
        else:
            pass
        new_string += chr(ascii_num)
    return new_string

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