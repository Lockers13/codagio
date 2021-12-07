ABC_LOWER = "abcdefghijklmnopqrstuvwxyz"
ABC_UPPER = ABC_LOWER.upper()

def rot13(inputs):
    ret_list = []
    for phrase in inputs:
        if not isinstance(phrase, str):
            ret_list.append("Error: input is not a string")
            continue
        out_phrase = ''
        for char in phrase:
            if char.isupper():
                out_phrase += ABC_UPPER[(ABC_UPPER.find(char)+13)%26]
            else:
                out_phrase += ABC_LOWER[(ABC_LOWER.find(char)+13)%26]
        ret_list.append(out_phrase)
    return ret_list