import ast
from collections import OrderedDict
import json
from pprint import pprint
import node_processors as npr

class FuncCallGetter(ast.NodeVisitor):
    func_call_dict = OrderedDict()
    def visit_Call(self, node):
        node_str = str(node)
        self.func_call_dict[node_str] = {}
        npr.process_call(node, self.func_call_dict)
        self.func_call_dict[node_str]["args"] = []
        for arg in node.args:
            if isinstance(arg, ast.Num):
                self.func_call_dict[node_str]["args"].append(arg.n)
            elif isinstance(arg, ast.Name):
                self.func_call_dict[node_str]["args"].append(arg.id)
            elif isinstance(arg, ast.Call):
                self.func_call_dict[arg] = {}
                npr.process_call(arg, self.func_call_dict)
            elif isinstance(arg, ast.BinOp):
                l, op, r = npr.process_binop(arg)
                bin_op_str = "{0} {1} {2}".format(l, op, r)
                self.func_call_dict[node_str]["args"].append(bin_op_str)
            elif isinstance(arg, ast.Str):
                str_message = "\"" + arg.s + "\""
                self.func_call_dict[node_str]["args"].append(str_message)

        self.generic_visit(node)

class FuncDefGetter(ast.NodeVisitor):
    func_def_dict = OrderedDict()
    def visit_FunctionDef(self, node):
        node_str = str(node)
        self.func_def_dict[node_str] = {}
        self.func_def_dict[node_str]["name"] = node.name
        self.func_def_dict[node_str]["retval"] = node.returns
        self.func_def_dict[node_str]["args"] = []
        for arg in node.args.args:
            self.func_def_dict[node_str]["args"].append(arg.arg)
        self.func_def_dict[node_str]["body"] = {}
        body_dict = self.func_def_dict[node_str]["body"]
        for body_node in node.body:
            npr.process_body(body_node, body_dict)

        self.generic_visit(node)

filename = "quicksort.py"
parsed_tree = ast.parse((open(filename)).read())

fcall_getter = FuncCallGetter()
fcall_getter.visit(parsed_tree)

print("Printing Function Call Info From Script : {0}".format(filename))
print("-------------------------------------------")
for k, v in fcall_getter.func_call_dict.items():
    print("{0}: {1}".format(k,v))
print()

fdef_getter = FuncDefGetter()
fdef_getter.visit(parsed_tree)

print("Printing Function Def Info From Script : {0}".format(filename))
print("-------------------------------------------")

for k, v in fdef_getter.func_def_dict.items():
    print("{0}: {1}".format(k,v))
    print()
