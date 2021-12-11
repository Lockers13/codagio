def rot13(inputs):
    ret_list = []
    ascii_lower = (97, 122)
    ascii_upper = (65, 90)
    LEN_ALPHA = 26
    for phrase in inputs:
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
        ret_list.append(new_string)
    return ret_list