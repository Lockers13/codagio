import ast
from collections import OrderedDict
import json
import subprocess
import os

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

    def __get_real_calls(self, fcalls):
        def any_key(keys, line):
            for key in keys:
                if fcalls[key]["name"] in line:
                    return [True, fcalls[key]["name"], key]
            return [False, None, None]

        fkeys = fcalls.keys()
        process = subprocess.Popen(["python", "-m", "cProfile", "-s", "time", "{0}".format(filename)], stdout=subprocess.PIPE)
        output = process.stdout.readlines()
        ### Note : watch for unintentionally long output ###
        for line in output:
            line = line.decode("utf-8").strip()
            key_guess = any_key(fkeys, line)
            if key_guess[0]:
                ncalls = line.split()[0]
                if ncalls == "ncalls":
                    continue
                fcalls[key_guess[2]]["real_calls"] = ncalls

    def __get_cpu_time(self, prog_dict):
        dev_null = open(os.devnull, 'w')
        process = subprocess.Popen(["time",  "-p", "python", "{0}".format(filename), "1>/dev/null"], stderr=subprocess.PIPE, stdout=dev_null)
        dev_null.close()
        output = process.stderr.readlines()
        for line in output:
            line = line.decode("utf-8").strip()
            split_line = line.split()
            prog_dict["{0} time".format(str(split_line[0]))] = split_line[1]

    def profile(self):
        self.__get_real_calls(self.program_dict["fcalls"])
        self.__get_cpu_time(self.program_dict)
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

filename = input(str("Please enter the name of a file to parse: "))

parsed_tree = ast.parse((open(filename)).read())

ast_visitor = AstTreeVisitor()

ast_visitor.visit(parsed_tree)

profiler = Profiler(filename, ast_visitor.program_dict)
profiler.profile()

rprint_dict(ast_visitor.program_dict)