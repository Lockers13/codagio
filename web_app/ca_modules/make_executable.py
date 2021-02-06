# import sys
# import os

def make_file(path, code):
    def write_prequel(file_obj):
        for line in IMPORTS:
            file_obj.write("{0}\n".format(line))
        file_obj.write("\n")

    def write_sequel(file_obj, fname):
        for line in TEMPLATE_CODE:
            if "template_function" in line:
                line = line.replace("template_function", str(fname))
            file_obj.write("{0}\n".format(line))

    IMPORTS = ["import json", 
                "import sys"]

    TEMPLATE_CODE = ["def prep_input():",
                    "    try:",
                    "        with open(sys.argv[1], 'r') as f:",
                    "            contents = json.loads(f.read())",
                    "        return contents[int(sys.argv[2])]",
                    "    except (IndexError, FileNotFoundError):",
                    "        print(\"Error: please make sure correct input has been provided\")",
                    "        sys.exit(1)\n",
                    "def main():",
                    "    input_list = prep_input()",
                    "    for inp in input_list:",
                    "        print(\"{0}\".format(template_function(inp)))\n",
                    "main()"]

    program_text = code.split("\n")

    with open(path, 'w') as f:
        write_prequel(f)
        for line in program_text:
            if line.startswith("def"):
                fname = line.split()[1].split("(")[0]
            f.write("{0}\n".format(line))
        if not line.endswith("\n"):
            f.write("\n")

        write_sequel(f, fname)
        
# if len(sys.argv) != 2:
#     print("Incorrect number of command line args...USAGE : python make_executable.py {scriptname}")
#     sys.exit(1)

# script_name = sys.argv[1]

# try:
#     make_dir = os.path.join("submissions", script_name.split(".")[0])
#     os.mkdir(make_dir)
# except FileExistsError:
#     pass
    

# script_path = os.path.join(make_dir, script_name)
# make_file(script_path)