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