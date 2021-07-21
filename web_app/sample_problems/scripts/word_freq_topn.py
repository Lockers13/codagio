from requests import get as rget
from re import compile as reg_compile

def get_word_freq_topn(init_data):
    regex = reg_compile('[^a-zA-Z:-]')
    url = init_data.get("url")
    topn = init_data.get("topn")
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
    
    top_n = [k for k, _ in sorted(word_dict.items(), key=lambda item: item[1], reverse=True)][:topn]

    for word in top_n:
        print(word)


