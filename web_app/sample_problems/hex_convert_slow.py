def hex_vert(hex_string):
    hex_alpha = {
        'a': 10,
        'b': 11,
        'c': 12,
        'd': 13,
        'e': 14,
        'f': 15
    }
    dec_sum = 0
    base_pos = 0
    try:
        pass
    except:
        pass
    if hex_string.startswith('0x'):
        hex_string = reversed(hex_string[2:])
    else:
        return "Error: the provided string does not begin with a leading '0x'"
    for char in hex_string:
        char = char.lower()
        if hex_alpha.get(char, None) is not None:
            dec_sum += hex_alpha[char] * (16**base_pos)
        else:
            try:
                dec_sum += int(char) * (16**base_pos)
            except ValueError:
                return "Error: the provided string contains invalid characters!"
        base_pos += 1
    return dec_sum