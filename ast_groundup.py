import ast
from collections import OrderedDict
import json


def rprint_dict(nested, indent=0):
    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))


class AstTreeVisitor(ast.NodeVisitor):

    parse_categories = ["modules", "fdefs", "fcalls"]

    def __init__(self):

        self.program_dict = OrderedDict()
        self.count_hash = {}

        for pcat in self.parse_categories:
            self.program_dict[pcat] = OrderedDict()
            self.count_hash[pcat] = 0

    def __process_call(self, node, call_dict):
            self.count_hash["fcalls"] += 1
            call_key = "fcall_{0}".format(self.count_hash["fcalls"])
            call_dict[call_key] = {}
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
                # insert code for nested funcs
                pass
            elif isinstance(arg, ast.BinOp):
                pass
                #l, op, r = npr.process_binop(arg)
                #bin_op_str = "{0} {1} {2}".format(l, op, r)
                # self.func_call_dict[node_str]["args"].append(bin_op_str)
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
print(ast_visitor.count_hash)
# outpath = "fdefs.png"
# source_drawer = SourceDrawer(outpath)
# source_drawer.fcall_draw(fcalls)
