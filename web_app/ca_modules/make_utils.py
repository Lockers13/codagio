### A module containing various utilities used at various points throughout the processes of submitting and analyzing problems ###

import os
import json
import subprocess
import hashlib
import sys
import random
import string
from .output_processor import process_output
from . import code_templates

def make_file(path, code, problem_data):
    """Function to create script that is used for verification and profiling purposes

    Returns nothing, writes to disk"""

    def write_prequel(file_obj):
        for line in ctemps["IMPORTS"]:
            file_obj.write("{0}\n".format(line))
        file_obj.write("\n")

    def write_sequel(file_obj, fname):
        if input_type == "file":
            if init_data is not None:
                text_to_write = ctemps["TEMPLATE_CODE_FILE_WITH_DATA"]
            else:
                text_to_write = ctemps["TEMPLATE_CODE_FILE"]
        elif input_type == "default": ### CHANGE 'auto' TO 'default' AFTER PROBLEM UPLOAD VIEW IS CLEANED !!!
            if is_inputs:
                if is_init_data:
                    text_to_write = ctemps["TEMPLATE_CODE_DEFAULT_WITH_INPUT_AND_DATA"]
                else:
                    text_to_write = ctemps["TEMPLATE_CODE_DEFAULT"]
            elif is_init_data:
                text_to_write = ctemps["TEMPLATE_CODE_DEFAULT"]

        for line in text_to_write:
            if "template_function" in line:
                line = line.replace("template_function", str(fname))
            file_obj.write("{0}\n".format(line))

    ctemps = code_templates.get_ctemp_dict()
    program_text = code
    input_type = list(problem_data["metadata"]["input_type"].keys())[0]
    main_function = problem_data["metadata"]["main_function"]
    init_data = problem_data["init_data"]
    is_init_data = problem_data["metadata"]["init_data"]
    is_inputs = problem_data["metadata"]["inputs"]

    with open(path, 'w') as f:
        write_prequel(f)
        for line in program_text:
            split_line = line.split()
            if len(split_line) > 0 and line.split()[0] == "def":
                func_name = line.split()[1].split("(")[0]
                if func_name == main_function:
                    fname = func_name
            f.write("{0}\n".format(line))
        if not line.endswith("\n"):
            f.write("\n")

        write_sequel(f, fname)

def gen_sample_outputs(filename, problem_data, init_data=None, input_type="default"):
    """Utility function invoked whenever a reference problem is submitted

    Returns a list of outputs that are subsequently stored in DB as field associated with given problem"""
    
    inputs = problem_data["inputs"]
    platform = sys.platform.lower()
    SAMPUP_TIMEOUT = "8"
    SAMPUP_MEMOUT = "1000"
    timeout_cmd = "gtimeout {0}".format(SAMPUP_TIMEOUT) if platform == "darwin" else "timeout {0}".format(SAMPUP_TIMEOUT) if platform == "linux" or platform == "linux2" else ""
    base_cmd = "{0} python".format(timeout_cmd)
    outputs = []
    if input_type == "default":
        programmatic_inputs = inputs
        if inputs is not None:
            for inp in programmatic_inputs:
                input_arg = json.dumps(inp) 
                output = process_output(base_cmd, filename, input_arg=input_arg, init_data=init_data)
                ### uncomment below line for debugging
                # print("CSO =>", cleaned_split_output)
                outputs.append(output)
        else:
            output = process_output(base_cmd, filename, init_data=init_data)
            ### uncomment below line for debugging
            # print("CSO =>", cleaned_split_output)
            outputs.append(output)
    elif input_type == "file":
        for script in inputs:
            output = process_output(base_cmd, filename, input_arg=script, init_data=init_data)
            ### uncomment below line for debugging
            # print("CSO =>", cleaned_split_output)
            outputs.append(output)
            try:
                os.remove(script)
            except:
                pass
    return outputs

def get_code_from_file(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def generate_input(input_type, input_length, num_tests):
    """Self-explanatory utility function that generates test input for a submitted reference problem based on metadata specifications

    Returns jsonified list of inputs"""
    
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
    return global_inputs

def handle_uploaded_file_inputs(processed_data):
    input_dict = {"files": {}}
    count = 0
    ### add below for loop for multiple files
    # for count, file_obj in enumerate(processed_data.get("target_file")):
    input_dict["files"]["file_{0}".format(count+1)] = ""
    file_obj = processed_data.get("target_file")
    with open("file_{0}.py".format(count+1), 'w') as g:
        for chunk in file_obj.chunks():
            decoded_chunk = chunk.decode("utf-8")
            input_dict["files"]["file_{0}".format(count+1)] += decoded_chunk
        g.write(decoded_chunk)
    return input_dict

def json_reorder(hashmap):
    new_hm = {}
    for k in sorted(hashmap, key=lambda item: (len(item), item), reverse=False):
        new_hm[k] = hashmap[k]
    return new_hm