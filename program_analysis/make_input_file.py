### change as needed!

import random
import string
import json 

LENGTH = 20
LETTERS = string.ascii_letters

def get_random_string():
    length = random.randint(1, LENGTH)
    result_str = ''.join(random.choice(LETTERS) for i in range(length))
    return result_str

global_str_list = []

for i in range(3):
    inner_str_list = [get_random_string() for i in range(1000)]
    global_str_list.append(inner_str_list)

with open('sample_problems/rot13/rot13_input.json', 'a') as f:
    f.write(json.dumps(global_str_list))
