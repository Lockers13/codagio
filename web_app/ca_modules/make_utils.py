import json
import subprocess
import hashlib
import sys
import random
import string

def make_file(path, code, source="web"):
    def write_prequel(file_obj):
        for line in IMPORTS:
            file_obj.write("{0}\n".format(line))
        file_obj.write("\n")

    def write_sequel(file_obj, fname):
        for line in TEMPLATE_CODE:
            if "template_function" in line:
                line = line.replace("template_function", str(fname))
            file_obj.write("{0}\n".format(line))


    IMPORTS = ["from json import loads as json_load", 
                "from sys import argv"]

    TEMPLATE_CODE = ["def prep_input():",
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
    
    if source == "web":  
        program_text = code.split("\n")
    elif source == "file":
        program_text = code
    elif source == "in_memory":
        program_text = [line.decode("utf-8") for line in code]
    else:
        print("ERROR: Unrecognized source type...exiting")
        sys.exit(1)

    with open(path, 'w') as f:
        write_prequel(f)
        for line in program_text:
            if line.startswith("def"):
                fname = line.split()[1].split("(")[0]
            f.write("{0}\n".format(line))
        if not line.endswith("\n"):
            f.write("\n")

        write_sequel(f, fname)

def gen_sample_hashes(filename, inputs):
    hashes = []
    programmatic_inputs = json.loads(inputs)
    for i in range(len(programmatic_inputs)):  
        s_process = subprocess.Popen(["python", filename, json.dumps(programmatic_inputs[i])], stdout=subprocess.PIPE)
        output = s_process.stdout.read().decode("utf-8")
        output = output.replace(' ', '').replace('\n', '')
        samp_hash = hashlib.md5(output.encode()).hexdigest()
        hashes.append(samp_hash)
    return hashes

def get_code_from_file(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

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