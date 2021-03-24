### A module containing various utilities used at various points throughout the processes of submitting and analyzing problems ###

import os
import json
import subprocess
import hashlib
import sys
import random
import string
from . import subprocess_ctrl as spc

def make_file(path, code, input_type="auto", init_data=False, main_function=None):
    """Function to create script that is used for verification and profiling purposes

    Returns nothing, writes to disk"""

    def write_prequel(file_obj):
        for line in IMPORTS:
            file_obj.write("{0}\n".format(line))
        file_obj.write("\n")

    def write_sequel(file_obj, fname):
        
        if input_type == "file":
            if init_data:
                text_to_write = TEMPLATE_CODE_FILE_WITH_DATA
            else:
                text_to_write = TEMPLATE_CODE_FILE 
        elif input_type == "auto":
            text_to_write = TEMPLATE_CODE_AUTO

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
                    "        template_function(argv[1])",
                    "    except Exception as e:",
                    "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                    "main()"]
    
    TEMPLATE_CODE_FILE_WITH_DATA = ["def main():",
                    "    try:",
                    "        template_function(argv[1], argv[2])",
                    "    except Exception as e:",
                    "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                    "main()"]

    program_text = code

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

def gen_sample_outputs(filename, inputs, init_data=None, input_type="auto"):
    """Utility function invoked whenever a reference problem is submitted

    Returns a list of outputs that are subsequently stored in DB as field associated with given problem"""
    
    platform = sys.platform.lower()
    SAMPUP_TIMEOUT = "5"
    SAMPUP_MEMOUT = "500"
    timeout_cmd = "gtimeout {0}".format(SAMPUP_TIMEOUT) if platform == "darwin" else "timeout {0} -m {1}".format(SAMPUP_TIMEOUT, SAMPUP_MEMOUT) if platform == "linux" or platform == "linux2" else ""
    base_cmd = "{0} python".format(timeout_cmd)
    outputs = []
    if input_type == "auto":
        programmatic_inputs = inputs
        for i in range(len(programmatic_inputs)):  
            output = spc.run_subprocess_ctrld(base_cmd, filename, json.dumps(programmatic_inputs[i]))
            cleaned_split_output = output.decode("utf-8").replace('\r', '').replace('None', '').splitlines()
            outputs.append(cleaned_split_output)
        return outputs
    elif input_type == "file":
        for script in inputs:
            if init_data is not None:
                output = spc.run_subprocess_ctrld(base_cmd, filename, script, init_data=init_data)
            else:
                output = spc.run_subprocess_ctrld(base_cmd, filename, script)
            cleaned_split_output = output.decode("utf-8").replace('\r', '').replace('None', '').splitlines()
            outputs.append(cleaned_split_output)
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
    files = []
    for count, file_obj in enumerate(processed_data.get("target_file")):
        input_dict["files"]["file_{0}".format(count+1)] = ""
        with open("file_{0}.py".format(count+1), 'w') as g:
            for chunk in file_obj.chunks():
                decoded_chunk = chunk.decode("utf-8")
                input_dict["files"]["file_{0}".format(count+1)] += decoded_chunk
            g.write(decoded_chunk)
            files.append("file_{0}.py".format(count+1))
    return input_dict, files

def json_reorder(hashmap):
    new_hm = {}
    for k in sorted(hashmap, key=lambda item: (len(item), item), reverse=False):
        new_hm[k] = hashmap[k]
    return new_hm