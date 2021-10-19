IMPORTS = ["from json import loads as json_load", 
            "from sys import argv"]

TEMPLATE_CODE_DEFAULT = ["def prep_input():",
                "    try:",
                "        return json_load(argv[1])",
                "    except IndexError:",
                "        print(\"Error: please make sure correct input has been provided\")",
                "        sys.exit(1)\n",
                "def main():",
                "    input_list_or_init_data = prep_input()",
                "    try:",
                "        print(\"{0}\".format(template_function(input_list_or_init_data)))",
                "        ### insert memprof ###",
                "    except Exception as e:",
                "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                "main()"]

TEMPLATE_CODE_DEFAULT_WITH_INPUT_AND_DATA = ["def prep_input():",
                "    try:",
                "        return json_load(argv[1]), json_load(argv[2])",
                "    except IndexError:",
                "        print(\"Error: please make sure correct input has been provided\")",
                "        sys.exit(1)\n",
                "def main():",
                "    input_list, init_data = prep_input()",
                "    try:",
                "        print(\"{0}\".format(template_function(input_list, init_data)))",
                "        ### insert memprof ###",
                "    except Exception as e:",
                "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                "main()"]

TEMPLATE_CODE_FILE = ["def prep_output():",
                "    try:",
                "        output = template_function(argv[1])",
                "        return output",
                "    except IndexError:",
                "        print(\"Error: please make sure correct input has been provided\")",
                "        sys.exit(1)\n",
                "def main():",
                "    try:",
                "        output = prep_output()",
                "        ### insert memprof ###",
                "        with open(argv[1], 'r') as f:",
                "            len_lines = len(f.readlines())",
                "        for i in range(1, len_lines+1):",
                "            if output.get(i, None) is not None:",
                "                print(i, output[i])",
                "            else:",
                "                print(i, False)",
                "    except Exception as e:",
                "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                "main()"]

TEMPLATE_CODE_FILE_WITH_DATA = ["def prep_output():",
                "    try:",
                "        data = json_load(argv[2])",
                "        targetfile = argv[1]",
                "        return template_function(targetfile, data)",
                "    except IndexError:",
                "        print(\"Error: please make sure correct input has been provided\")",
                "def main():",
                "    try:",
                "        output = prep_output()",
                "        ### insert memprof ###",
                "        if isinstance(output, dict):",
                "            with open(argv[1], 'r') as f:",
                "                len_lines = len(f.readlines())",
                "            for i in range(1, len_lines+1):",
                "                if output.get(i, None) is not None:",
                "                    print(i, output[i])",
                "                else:",
                "                    print(i, False)",
                "        elif isinstance(output, list):",
                "            for line in output:",
                "                print(line)",
                "    except Exception as e:",
                "        print('EXCEPTION: semantic error in submitted program: {0}'.format(str(e)))\n",
                "main()"]


def get_ctemp_dict():

    ctemps = {
        "IMPORTS": IMPORTS,
        "TEMPLATE_CODE_DEFAULT": TEMPLATE_CODE_DEFAULT,
        "TEMPLATE_CODE_DEFAULT_WITH_INPUT_AND_DATA": TEMPLATE_CODE_DEFAULT_WITH_INPUT_AND_DATA,
        "TEMPLATE_CODE_FILE": TEMPLATE_CODE_FILE,
        "TEMPLATE_CODE_FILE_WITH_DATA": TEMPLATE_CODE_FILE_WITH_DATA,
    }
    
    return ctemps