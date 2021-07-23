from requests import get as rget
from re import compile as reg_compile

def get_word_freq(inputs, init_data):
    url = init_data.get("url")
    regex = reg_compile('[^a-zA-Z:-]')
    data = rget(url).text
    word_dict = {}
    for word in data.split():
        try:
            word.encode("ascii")
        except UnicodeEncodeError:
            continue
        word = word.lower()
        if word.endswith(',') or word.endswith('.'):
            word = word[:-1]
        if regex.search(word):
            continue
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1
    
    for word in inputs:
        freq = word_dict.get(word, 0)
        print("{0} : {1}".format(word, freq))
