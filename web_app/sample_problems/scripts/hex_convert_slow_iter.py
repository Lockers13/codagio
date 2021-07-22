hex_alpha = {
        'a': 10,
        'b': 11,
        'c': 12,
        'd': 13,
        'e': 14,
        'f': 15
    }

def hex_vert(inputs):
    for hex_string in inputs:
        orig_hex_string = hex_string
        if hex_string.startswith('0x'):
            hex_string = reversed(hex_string[2:])
        else:
            print("{0} : {1}".format(hex_string, "Error: does not begin with a leading '0x'"))
            continue
        res = scan_chars(hex_string)
        print("{0} : {1}".format(orig_hex_string, res))

def scan_chars(hex_string):
    dec_sum = 0
    base_pos = 0
    for char in hex_string:
        char = char.lower()
        if hex_alpha.get(char, None) is not None:
            dec_sum += hex_alpha[char] * (16**base_pos)
        else:
            try:
                dec_sum += int(char) * (16**base_pos)
            except ValueError:
                return "Error: invalid characters!"
        base_pos += 1
    return dec_sum
