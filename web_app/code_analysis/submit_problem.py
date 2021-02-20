import os
import sys
import json
from .models import Problem
from ca_modules.analyzer import Analyzer
from ca_modules import make_utils
from datetime import datetime
import random
import string

def generate_input(input_type, input_length, num_tests):
    def random_string(length):
        rand_string = ''.join(random.choice(string.ascii_letters) for i in range(length))
        return rand_string

    global_inputs = []

    for i in range(num_tests):
        if input_type == "integer":
            inp_list = [random.randint(1, 1000) for x in range(input_length)]
        elif input_type == "float":
            inp_list = [round(random.uniform(0.0, 1000.0), 2) for x in range(input_length)]
        elif input_type == "string":
            inp_list = [random_string(random.randint(1, 10)) for x in range(input_length)]
        global_inputs.append(inp_list)
    return json.dumps(global_inputs)
    
def create_problem(get_dict):
    input_type = get_dict.get('it')
    input_length = 1000
    num_tests = 3
    filename = os.path.join(os.getcwd(), "sample_problems", get_dict.get("fn"))
    prob_name = os.path.basename(filename).split(".")[0]
    difficulty = get_dict.get('diff')
    desc = get_dict.get('desc')
    analyzer = Analyzer(filename)
    analyzer.visit_ast()
    json_inputs = generate_input(input_type, input_length, num_tests)
    analyzer.profile(json_inputs, solution=False)
    analysis = json.dumps(analyzer.get_prog_dict())
    hashes = make_utils.gen_sample_hashes(filename, json_inputs)
    problem, created = Problem.objects.update_or_create(
        defaults = {
            'difficulty': difficulty,
            'hashes': json.dumps(hashes),
            'date_created': datetime.now(),
            'author_id': 7,
            'desc': desc,
            'name': prob_name,
            'inputs': json_inputs,
            'analysis': analysis
        }
    )
    problem.save()