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

str_list = [get_random_string() for i in range(1000)]

with open('../web_app/sample_problems/misc_inputs/rot13_input.json', 'w') as f:
    f.write(json.dumps(str_list))
