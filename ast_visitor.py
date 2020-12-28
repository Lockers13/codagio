import ast
from collections import OrderedDict

class AstTreeVisitor(ast.NodeVisitor):

    __parse_categories = ["modules", "fdefs", "fcalls", "whiles", "ifs", "fors"]

    __bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

    def __init__(self):
        self.program_dict = OrderedDict()
        self.count_hash = {}
        for pcat in self.__parse_categories:
            self.program_dict[pcat] = OrderedDict()
            self.count_hash[pcat] = 0
        self.count_hash["level"] = 0

    def __process_while(self, node, node_dict, nested=False):
        while_id = "{0}_{1}".format(type(node).__name__.lower(), self.count_hash["whiles"])
        node_dict[while_id] = {}
        node_dict[while_id]["lineno"] = node.lineno
        node_dict[while_id]["level"] = self.count_hash["level"]
        node_dict[while_id]["body"] = {}
        body_dict = node_dict[while_id]["body"]
        body_dict["test_type"] = type(node.test).__name__.lower()
        body_dict["nested"] = nested
        self.__process_body(node, body_dict)


    def __process_if(self, node, node_dict):
        if_id = "{0}_{1}".format(type(node).__name__.lower(), self.count_hash["ifs"])
        node_dict[if_id] = {}
        node_dict[if_id]["lineno"] = node.lineno
        node_dict[if_id]["level"] = self.count_hash["level"]
        node_dict[if_id]["body"] = {}
        body_dict = node_dict[if_id]["body"]
        body_dict["test_type"] = type(node.test).__name__.lower()
        self.__process_body(node, body_dict)

    def __process_for(self, node, node_dict, nested=False):
        for_id = "{0}_{1}".format(type(node).__name__.lower(), self.count_hash["fors"])
        node_dict[for_id] = {}
        node_dict[for_id]["lineno"] = node.lineno
        node_dict[for_id]["level"] = self.count_hash["level"]
        node_dict[for_id]["body"] = {}
        body_dict = node_dict[for_id]["body"]
        body_dict["nested"] = nested
        self.__process_body(node, body_dict)

    def __process_body(self, node, node_dict):
        self.count_hash["level"] += 1
        for body_node in node.body:
            if isinstance(body_node, ast.While):
                self.count_hash["whiles"] += 1
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_while(body_node, node_dict, nested)
            elif isinstance(body_node, ast.For):
                self.count_hash["fors"] += 1
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_for(body_node, node_dict, nested)
            elif isinstance(body_node, ast.If):
                self.count_hash["ifs"] += 1
                self.__process_if(body_node, node_dict)
            else:
                node_dict["op"] = type(body_node).__name__.lower()
        self.count_hash["level"] -= 1

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
        body_dict = fdef_dict[fdef_key]["body"]

        self.__process_body(node, body_dict)

        
        # FOR LOOPS
        # print("ENDFUNC =>", node.body[-1]lineno)
        ### process body ###
        self.generic_visit(node)