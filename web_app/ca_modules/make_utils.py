### A module containing various utilities used at various points throughout the processes of submitting and analyzing problems ###

import os
import json
import subprocess
import hashlib
import sys
import random
import string

def make_file(path, code, source="web", input_type="auto"):
    """Function to create script that is used for verification and profiling purposes

    Returns nothing, writes to disk"""

    def write_prequel(file_obj):
        for line in IMPORTS:
            file_obj.write("{0}\n".format(line))
        file_obj.write("\n")

    def write_sequel(file_obj, fname):
        text_to_write = TEMPLATE_CODE_FILE if input_type == "file" else TEMPLATE_CODE_AUTO
        for line in text_to_write:
            if "template_function" in line:
                line = line.replace("template_function", str(fname))
            file_obj.write("{0}\n".format(line))


    IMPORTS = ["from json import loads as json_load", 
                "from sys import argv"]

    TEMPLATE_CODE_AUTO = ["def prep_input():",
                    "    try:",
                    "        return json_load(argv[1])",
                    "    except IndexError:",
                    "        print(\"Error: please make sure correct input has been provided\")",
                    "        sys.exit(1)\n",
                    "def main():",
                    "    input_list = prep_input()",
                    "    try:",
                    "        for inp in input_list:",
                    "            print(\"{0} {1}\".format(inp, template_function(inp)))",
                    "    except Exception as e:",
                    "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                    "main()"]
    
    TEMPLATE_CODE_FILE = ["def main():",
                    "    try:",
                    "        print(\"{0}\".format(template_function(argv[1])))",
                    "    except Exception as e:",
                    "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                    "main()"]

    if source == "web":  
        program_text = code.split("\n")
    elif source == "file":
        program_text = code
    else:
        raise Exception("ERROR: Unrecognized source type...exiting")

    with open(path, 'w') as f:
        write_prequel(f)
        for line in program_text:
            split_line = line.split()
            if len(split_line) > 0 and line.split()[0] == "def":
                fname = line.split()[1].split("(")[0]
            f.write("{0}\n".format(line))
        if not line.endswith("\n"):
            f.write("\n")

        write_sequel(f, fname)

def gen_sample_hashes(filename, inputs, input_type="auto"):
    """Utility function invoked whenever a reference problem is submitted

    Returns a list of output hashes that are subsequently stored in DB as field associated with given problem"""
    
    def process_output(output, hashes):
        output = output.replace(' ', '').replace('\n', '').replace('None', '') ### <= unsure why this is necessary??
        samp_hash = hashlib.md5(output.encode()).hexdigest()
        hashes.append(samp_hash)

    hashes = []
    if input_type == "auto":
        programmatic_inputs = json.loads(inputs)
        for i in range(len(programmatic_inputs)):  
            s_process = subprocess.Popen(["python", filename, json.dumps(programmatic_inputs[i])], stdout=subprocess.PIPE)
            output = s_process.stdout.read().decode("utf-8")
            process_output(output, hashes)
        return hashes
    elif input_type == "file":
        for script in inputs:
            s_process = subprocess.Popen(["python", filename, script], stdout=subprocess.PIPE)
            output = s_process.stdout.read().decode("utf-8")
            process_output(output, hashes)
        return hashes

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
    return json.dumps(global_inputs)

def handle_uploaded_file_inputs(processed_data):
    input_dict = {"files": {}}
    files = []
    for count, file_obj in enumerate(processed_data.get("input_files")):
        input_dict["files"]["file_{0}".format(count+1)] = ""
        with open("file_{0}.py".format(count+1), 'w') as g:
            for chunk in file_obj.chunks():
                decoded_chunk = chunk.decode("utf-8")
                input_dict["files"]["file_{0}".format(count+1)] += decoded_chunk
            g.write(decoded_chunk)
            files.append("file_{0}.py".format(count+1))
    return json.dumps(input_dict), files