import ast
from collections import OrderedDict
import json

bin_ops = {"Add": '+',
           "Sub": '-',
           "Mult": '*',
           "Div": '/',
           "FloorDiv": "//",
           "Mod": '%',
           "Pow": "**",
           "LShift": "<<",
           "RShift": ">>",
           "BitOr": '|',
           "BitXor": '^',
           "BitAnd": '&',
           "MatMult": '@',
           "Lt": '<',
           "Gt": '>'}

def process_call(call_node, fcd):
    if isinstance(call_node.func, ast.Name):
        fcd[call_node]["name"] = call_node.func.id
        fcd[call_node]["lineno"] = call_node.func.lineno
    else:
        fcd[call_node]["name"] = call_node.func.attr
        fcd[call_node]["lineno"] = call_node.func.lineno

def process_body(body_node, body_dict):
    if isinstance(body_node, ast.For):
        body_dict["for"] = {}
        body_dict["for"]["iter"] = vars(body_node.iter)
        body_dict["for"]["target"] = vars(body_node.target)
    elif isinstance(body_node, ast.While):
        body_dict["while"] = {}
        body_dict["while"]["test"] = []
        body_dict["while"]["test"].append(vars(body_node.test))
        body_dict["while"]["body"] = {}
        inner_body_dict = body_dict["while"]["body"]
        for i in body_node.body:
            process_body(i, inner_body_dict)
    elif isinstance(body_node, ast.While):
        body_dict["while"] = {}
        body_dict["while"]["test"] = vars(body_node.test)
    elif isinstance(body_node, ast.If):
        body_dict["if"] = {}
        body_dict["if"]["test"] = {}
        if_test = body_dict["if"]["test"]
        process_test(body_node.test, if_test)
    elif isinstance(body_node, ast.Try):
        body_dict["try"] = {}
        body_dict["try"]["body"] = {}
        body_dict["try"]["body"]["type"] = []
        for i in body_node.body:
            body_dict["try"]["body"]["type"].append(type(i).__name__)
            ### Continue here with with --- process_body(i, body_dict["try"]["body"])


def process_test(test, test_dict):
    global bin_ops
    test_vars = vars(test)
    for key in test_vars.keys():
        try:
            obj = test_vars[key][0]
            if isinstance(obj, ast.Name):
                if key == "comparators":
                    test_dict["comp"] = vars(obj)
            else:
                test_dict["ops"] = bin_ops[type(obj).__name__]
        except:
            if isinstance(test_vars[key], ast.Name):
                if key == "left":
                    test_dict["left"] = test_vars[key].id

def process_binop(arg):
    global bin_ops
    binop_list = []
    for i in range(3):
        vargs = list(vars(arg).values())
        if isinstance(vargs[i], ast.Name):
            binop_list.append(vargs[i].id)
        elif isinstance(vargs[i], ast.Num):
            binop_list.append(vargs[i].n)
        else:
            try:
                binop_list.append(bin_ops[type(vargs[i]).__name__])
            except:
                binop_list.append(str(vargs[i]))

    return binop_list

class FuncCallGetter(ast.NodeVisitor):
    func_call_dict = OrderedDict()
    def visit_Call(self, node):

        self.func_call_dict[node] = {}
        process_call(node, self.func_call_dict)
        self.func_call_dict[node]["args"] = []
        for arg in node.args:
            if isinstance(arg, ast.Num):
                self.func_call_dict[node]["args"].append(arg.n)
            elif isinstance(arg, ast.Name):
                self.func_call_dict[node]["args"].append(arg.id)
            elif isinstance(arg, ast.Call):
                self.func_call_dict[arg] = {}
                process_call(arg, self.func_call_dict)
            elif isinstance(arg, ast.BinOp):
                l, op, r = process_binop(arg)
                bin_op_str = "{0} {1} {2}".format(l, op, r)
                self.func_call_dict[node]["args"].append(bin_op_str)
            elif isinstance(arg, ast.Str):
                str_message = "\"" + arg.s + "\""
                self.func_call_dict[node]["args"].append(str_message)

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
            process_body(body_node, body_dict)

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
