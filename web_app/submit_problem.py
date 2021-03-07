import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
import os
import sys
import json
from code_analysis.models import Problem
from ca_modules.analyzer import Analyzer
from ca_modules import make_utils
from datetime import datetime
import random
import string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import getpass


    
def create_problem():
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
    
    name = input("Please enter your username: ")
    user = User.objects.filter(username=name).first()
    uid = user.id
    if not user.is_superuser:
        print("Sorry, only admins can submit problems, exiting...")
        sys.exit(2)
    else:
        tries = 0
        while tries < 3:
            password = getpass.getpass(prompt="Please enter your password: ")
            if not authenticate(username=name, password=password):
                print("Incorrect password, please try again.")
                tries += 1
            else:
                break
        if tries > 2:
            print("Three attempts failed, exiting...")
            sys.exit(3)

    input_type = input("Input Type: ")
    input_length = int(input("Input Length: "))
    num_tests = int(input("# Tests: "))
    metafile = os.path.join(os.getcwd(), "sample_problems", input("Metadata file: "))
    fname = os.path.join(os.getcwd(), "sample_problems", input("Script Name: "))
    prob_name = os.path.basename(fname).split(".")[0]
    # difficulty = input("Problem Difficulty: ")
    # desc = input("Problem Description: ")
    with open(metafile, 'r') as f:
        metadata = json.loads(f.read())
    code = make_utils.get_code_from_file(fname)
    filename = "{0}.py".format(prob_name)
    make_utils.make_file(filename, code, source="file")
    metadata["date_created"] = datetime.now()
    metadata["constraints"]["allowed_rel_imports"]["sys"] = ["argv"]
    metadata["constraints"]["allowed_rel_imports"]["json"] = ["loads"]
    analyzer = Analyzer(filename, metadata)
    analyzer.visit_ast()
    json_inputs = generate_input(input_type, input_length, num_tests)
    analyzer.profile(json_inputs, solution=False)
    analysis = json.dumps(analyzer.get_prog_dict())
    hashes = make_utils.gen_sample_hashes(filename, json_inputs)
    problem, created = Problem.objects.update_or_create(
        name=prob_name, author_id=uid,
        defaults = {
            'hashes': json.dumps(hashes),
            'metadata': json.dumps(metadata, default=str),
            'inputs': json_inputs,
            'analysis': analysis
        }
    )
    problem.save()

    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

create_problem()