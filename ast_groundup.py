import ast
from collections import OrderedDict
import json
import subprocess
import re

def rprint_dict(nested, indent=0):
    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))

def get_real_calls(filename, fcalls):
    def any_key(keys, line):
        for key in keys:
            if fcalls[key]["func"]["name"] in line:
                return [True, fcalls[key]["func"]["name"]]
        return [False, None]

    fileput = '{0}_profile.txt'.format(filename.split(".")[0])
    with open(fileput, 'w') as output:
        subprocess.Popen(["python", "-m", "cProfile", "-s", "time", "{0}".format(filename)], stdout=output).wait()
    with open(fileput, 'r') as f:
        fkeys = fcalls.keys()
        for line in f.readlines():
            key_guess = any_key(fkeys, line)
            if key_guess[0]:
                ncalls = line.split()[0]
                if ncalls == "ncalls":
                    continue
                print("No. of real calls of '{0}' in {1} = {2}".format(key_guess[1], filename, ncalls))
            



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
        call_dict[call_key]["func"] = {}
        func_details = call_dict[call_key]["func"]
        if isinstance(node.func, ast.Name):
            func_details["name"] = node.func.id
            func_details["lineno"] = node.func.lineno
        else:
            func_details["name"] = node.func.attr
            func_details["lineno"] = node.func.lineno

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
        self.generic_visit(node)


filename = input(str("Please enter the name of a file to parse: "))

parsed_tree = ast.parse((open(filename)).read())

ast_visitor = AstTreeVisitor()
ast_visitor.visit(parsed_tree)

mods = ast_visitor.program_dict.get("modules")
fcalls = ast_visitor.program_dict.get("fcalls")
fdefs = ast_visitor.program_dict.get("fdefs")

print("\nProcessing Script: {0}...".format(filename))

print("\n\n**************** Module Info ****************\n\n")
rprint_dict(mods)

print("\n\n**************** Function Def Info ****************\n\n")
rprint_dict(fdefs)

print("\n\n**************** Function Call Info ****************\n\n")
rprint_dict(fcalls)
print("No. of distinct function calls in source =", ast_visitor.count_hash["fcalls"])
print()
get_real_calls(filename, fcalls)

# outpath = "fdefs.png"
# source_drawer = SourceDrawer(outpath)
# source_drawer.fcall_draw(fcalls)
