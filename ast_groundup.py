import ast
from collections import OrderedDict
import json
import subprocess
import os
import argparse
import platform
import re

def parse_clargs():
    ap = argparse.ArgumentParser() 
    ap.add_argument("-m", action="store_true")
    return vars(ap.parse_args())

def rprint_dict(nested, indent=0):
    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))

class Profiler():

    def __init__(self, filename, program_dict):
        self.filename = filename
        self.program_dict = program_dict

    def __lprof(self):
        ### Note: check if line_profiler is installed
        def get_user_fdefs():
            udef_lines = []
            fdef_dict = self.program_dict.get("fdefs")
            fdef_keys = fdef_dict.keys()
            for fdef_key in fdef_keys:
                udef_lines.append(fdef_dict[fdef_key]["lineno"])
            return udef_lines
        
        def make_pro_file(filename, lines, token):
            f = open(filename, "r")
            contents = f.readlines()
            f.close()

            profiled_lines = 0

            for lineno in lines:
                contents.insert((lineno-1) + profiled_lines, "{0}\n".format(token))
                profiled_lines += 1

            split_fname = filename.split(".")
            pro_file = "{0}_profile.{1}".format(split_fname[0],split_fname[1])
            f = open(pro_file, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()

            return pro_file

        def parse_pro_file(pro_file):
            def write_lprofs():
                float(second_item)
                fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)] = {}
                line_info = fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)]
                line_info["hits"] = split_line[1]
                line_info["time"] = '%.2E' % (float(split_line[2]) * time_unit)
                line_info["time_per_hit"] = '%.2E' % (float(split_line[3]) * time_unit)
                line_info["%time"] = split_line[4]
                line_info["contents"] = split_line[5]

            process = subprocess.Popen(["kernprof", "-l", "-v", "{0}".format(pro_file)], stdout=subprocess.PIPE)
            output = process.stdout.readlines()
            fdefs = self.program_dict["fdefs"]
            fdef_keys = fdefs.keys()

            for line in output:
                line = line.decode("utf-8").strip()
                split_line = line.split(maxsplit=5)

                try:
                    first_item, second_item = split_line[0], split_line[1]
                except IndexError:
                    continue

                if split_line[1] == "unit:":
                    time_unit = float(split_line[2])

                if len(split_line) == 6 or first_item == "Total" or first_item == "Function:":
                    if first_item == "Total":
                        total_time = split_line[2]
                    elif first_item == "Function:":
                        fname = split_line[1]
                        for fdef_key in fdef_keys:
                            if fdefs[fdef_key]["name"] == fname:
                                fdef_k = fdef_key 
                                fdefs[fdef_k]["line_profile"] = {}
                                fdefs[fdef_k]["total_time (lprof)"] = total_time
                                fnum = int(re.search(r'\d+', fdef_k).group())
                    else:
                        try:
                            write_lprofs()
                        except ValueError:
                            continue
                else:
                    continue
        
        try:
            import line_profiler
        except ModuleNotFoundError:
            print("Error: line_profiler module must be installed for line-by-line profiling!")
            return

        udef_lines = get_user_fdefs()
        pro_token = "@profile"
        pro_file = make_pro_file(self.filename, udef_lines, pro_token)
        parse_pro_file(pro_file)

            ### Line_Profiler output header => Line #: Hits: Time: Per Hit: % Time: Line Contents
            

    def __cprof(self):
        pass
        def any_key(keys, line):
            for key in keys:
                if fcalls[key]["name"] in line:
                    return [True, fcalls[key]["name"], key]
            return [False, None, None]

    #     fcalls = self.program_dict.get("fcalls")
    #     fkeys = fcalls.keys()
        process = subprocess.Popen(["python", "-m", "cProfile", "-s", "time", "{0}".format(filename)], stdout=subprocess.PIPE)
        output = process.stdout.readlines()
        ### Note : watch for unintentionally long output ###
        for line in output:
            line = line.decode("utf-8").strip()
            print(line)
    #         key_guess = any_key(fkeys, line)
    #         if key_guess[0]:
    #             ncalls = line.split()[0]
    #             if ncalls == "ncalls":
    #                 continue
    #             ### add more info, or delete altogether!!!
    #             fcalls[key_guess[2]]["real_calls"] = ncalls

    def __gnu_time(self):
        time_cmd = "gtime" if platform.system() == "Darwin" else "time"
        prog_dict = self.program_dict
        dev_null = open(os.devnull, 'w')
        process = subprocess.Popen([time_cmd,  "--verbose", "python", "{0}".format(filename)], stderr=subprocess.PIPE, stdout=dev_null)
        dev_null.close()
        output = process.stderr.readlines()
        for line in output:
            line = line.decode("utf-8").strip()
            split_line = line.split(": ")
            try:
                prog_dict["{0}".format(str(split_line[0]))] = float(split_line[1])
            except ValueError:
                pass

    def profile(self):
        self.__cprof()
        self.__gnu_time()
        self.__lprof()
        ### And so on ###    

class AstTreeVisitor(ast.NodeVisitor):

    __parse_categories = ["modules", "fdefs", "fcalls"]

    __bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

    def __init__(self):
        self.program_dict = OrderedDict()
        self.count_hash = {}
        for pcat in self.__parse_categories:
            self.program_dict[pcat] = OrderedDict()
            self.count_hash[pcat] = 0
            
    def __process_binop(self, arg):
        binop_list = []
        for i in range(3):
            vargs = list(vars(arg).values())
            if isinstance(vargs[i], ast.Name):
                binop_list.append(vargs[i].id)
            elif isinstance(vargs[i], ast.Num):
                binop_list.append(vargs[i].n)
            elif isinstance(vargs[i], ast.Str):
                binop_list.append(vargs[i].s)
            else:
                try:
                    binop_list.append(self.__bin_ops[type(vargs[i]).__name__])
                except:
                    binop_list.append(str(vargs[i]))
        return binop_list

    def __process_call(self, node, call_dict, parent=None):
        self.count_hash["fcalls"] += 1
        call_key = "fcall_{0}".format(self.count_hash["fcalls"])
        call_dict[call_key] = {}
        call_dict[call_key]["parent"] = parent
        self.__process_args(node.args, call_dict[call_key])
        if isinstance(node.func, ast.Name):
            call_dict[call_key]["name"] = node.func.id
            call_dict[call_key]["lineno"] = node.func.lineno
        else:
            call_dict[call_key]["name"] = node.func.attr
            call_dict[call_key]["lineno"] = node.func.lineno

    def __process_args(self, arg_node, call_dict):
        call_dict["args"] = []
        for arg in arg_node:
            if isinstance(arg, ast.Num):
                call_dict["args"].append(arg.n)
            elif isinstance(arg, ast.Name):
                call_dict["args"].append(arg.id)
            elif isinstance(arg, ast.Call):
                arg_func = "arg_func_{0}".format(self.count_hash["fcalls"])
                call_dict[arg_func] = {}
                self.__process_call(arg, call_dict[arg_func], "{0}".format(self.count_hash["fcalls"]))
            elif isinstance(arg, ast.BinOp):
                l, op, r = self.__process_binop(arg)
                bin_op_str = "{0} {1} {2}".format(l, op, r)
                call_dict["args"].append(bin_op_str)
            elif isinstance(arg, ast.Str):
                str_message = "\"" + arg.s + "\""
                call_dict["args"].append(str_message)

    def visit_Call(self, node):
        self.__process_call(node, self.program_dict["fcalls"])
        self.generic_visit(node)

    def visit_Module(self, node):
        mod_dict = self.program_dict["modules"]
        self.count_hash["modules"] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        fdef_dict = self.program_dict["fdefs"]
        self.count_hash["fdefs"] += 1
        fdef_key = "fdef_{0}".format(self.count_hash["fdefs"])
        fdef_dict[fdef_key] = {}
        fdef_dict[fdef_key]["name"] = node.name
        fdef_dict[fdef_key]["retval"] = node.returns
        fdef_dict[fdef_key]["lineno"] = node.lineno
        fdef_dict[fdef_key]["args"] = []
        for arg in node.args.args:
            fdef_dict[fdef_key]["args"].append(arg.arg)
        fdef_dict[fdef_key]["body"] = {}
        ### process body ###
        self.generic_visit(node)

args = parse_clargs()
# filename = input(str("Please enter the name of a file to parse: "))
filename = "quicksort.py"
parsed_tree = ast.parse((open(filename)).read())

ast_visitor = AstTreeVisitor()
ast_visitor.visit(parsed_tree)

profiler = Profiler(filename, ast_visitor.program_dict)
profiler.profile()

rprint_dict(ast_visitor.program_dict)