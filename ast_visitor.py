import ast
from collections import OrderedDict

class AstTreeVisitor(ast.NodeVisitor):
    """Class for visiting ast tree"""

    # private instance var determining what entries to create in prog dict
    __parse_categories = ["modules", "fdefs", "fcalls", "whiles", "ifs", "fors", "assigns", "aug_assigns", "calls"]

    # binary operation hash map, needed for translating AST's binop objects to more readable form
    __bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

    def __init__(self):
        self.program_dict = OrderedDict()
        self.count_hash = {}
        for pcat in self.__parse_categories:
            self.program_dict[pcat] = OrderedDict()
            self.count_hash[pcat] = 0
        # count var to record indentation level
        self.count_hash["level"] = -1
        # count var to record num ops
        self.count_hash["ops"] = 0
        self.fname = None
    
    def __prep_body_dict(self, node, node_dict, count_key):
        """Utility method to initialize body_dict.

        Returns initialized body dict"""

        # create unique identifier key for any body elem
        identifier = "{0}_{1}".format(type(node).__name__.lower(), self.count_hash[count_key])
        node_dict[identifier] = OrderedDict()
        node_dict[identifier]["lineno"] = node.lineno
        node_dict[identifier]["level"] = self.count_hash["level"]
        node_dict[identifier]["body"] = {}
        return node_dict[identifier]["body"]

    def __process_while(self, node, node_dict, nested=False):
        """Utility method to recursively process any 'while' constructs encountered in AST tree,
        where by 'process' we mean => write pertinent info to appropriate place in prog dict.
        Note: all such helper methods call '__process_body()' for the purposes of exploiting 
        the intrinsically recursive nature of the AST tree.

        Returns None"""

        body_dict = self.__prep_body_dict(node, node_dict, "whiles")
        body_dict["test_type"] = type(node.test).__name__.lower()
        body_dict["nested"] = nested
        self.__process_body(node, body_dict)

    def __process_if(self, node, node_dict):
        """Utility method to recursively process any 'if' constructs encountered in AST tree.

        Returns None"""

        body_dict = self.__prep_body_dict(node, node_dict, "ifs")
        body_dict["test_type"] = type(node.test).__name__.lower()
        self.__process_body(node, body_dict)

    def __process_for(self, node, node_dict, nested=False):
        """Utility method to recursively process any 'for' constructs encountered in AST tree.

        Returns None"""

        body_dict = self.__prep_body_dict(node, node_dict, "fors")
        body_dict["nested"] = nested
        self.__process_body(node, body_dict)

    def __process_body(self, node, node_dict):
        """Utility method to recursively process the body of any given AST construct containing a body. 
        At the highest level, we start by processing the body of function definitions, then the bodies 
        of any while/for/if, etc., nodes encountered therein, and so on and so forth, until we reach a node with no body, 
        in which case we simply write the name of the node ('type(node).__name__'), and some other basic info.,
        to our prog dict and return None.
        
        Returns None"""

        self.count_hash["level"] += 1
        for body_node in node.body:
            if isinstance(body_node, ast.While):
                self.count_hash["whiles"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_whiles"] += 1
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_while(body_node, node_dict, nested)
            elif isinstance(body_node, ast.For):
                self.count_hash["fors"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_fors"] += 1
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_for(body_node, node_dict, nested)
            elif isinstance(body_node, ast.If):
                self.count_hash["ifs"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_ifs"] += 1
                self.__process_if(body_node, node_dict)
            elif isinstance(body_node, ast.Expr):
                if isinstance(body_node.value, ast.Call):
                    self.count_hash["calls"] += 1
                    self.program_dict["fdefs"][self.fdef_key]["num_calls"] += 1
                    self.__process_call(body_node.value, node_dict)
                else:
                    node_dict["expr"] = type(body_node.value).__name__
            elif isinstance(body_node, ast.FunctionDef):
                pass
            else:
                self.count_hash["ops"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_ops"] += 1
                node_key = "op_{0}".format(self.count_hash["ops"])
                node_dict[node_key] = {}
                try:
                    value = body_node.value
                    if isinstance(value, ast.Call):
                        self.__process_call(body_node.value, node_dict)
                    node_dict[node_key]["value"] = type(value).__name__.lower()
                except:
                    value = vars(body_node)
                    node_dict[node_key]["value"] = value
                node_dict[node_key] = {
                    "type": type(body_node).__name__.lower(),
                    "lineno": body_node.lineno,
                    "level": self.count_hash["level"]
                }
                     
        self.count_hash["level"] -= 1

    def __process_binop(self, arg):
        """Utility method to make AST BinOp constructs more readable.

        Returns binop_list => e.g. ['a', '**', '2']"""

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
        """Utility method to recursively process any 'call' constructs encountered in AST tree.

        Returns None"""

        self.count_hash["fcalls"] += 1
        call_key = "fcall_{0}".format(self.count_hash["fcalls"])
        call_dict[call_key] = {}
        call_dict[call_key]["param_caller"] = parent
        self.__process_args(node.args, call_dict[call_key])
        if isinstance(node.func, ast.Name):
            call_dict[call_key]["name"] = node.func.id
            call_dict[call_key]["lineno"] = node.func.lineno
        else:
            call_dict[call_key]["name"] = node.func.attr
            call_dict[call_key]["lineno"] = node.func.lineno

    def __process_args(self, arg_node, call_dict):
        """Utility method for processing encountered function or method parameters/args.

        Returns None"""

        call_dict["params"] = []
        for arg in arg_node:
            if isinstance(arg, ast.Num):
                call_dict["params"].append(arg.n)
            elif isinstance(arg, ast.Name):
                call_dict["params"].append(arg.id)
            elif isinstance(arg, ast.Call):
                arg_func = "arg_func_{0}".format(self.count_hash["fcalls"])
                call_dict[arg_func] = {}
                self.__process_call(arg, call_dict[arg_func], "{0}".format(self.count_hash["fcalls"]))
            elif isinstance(arg, ast.BinOp):
                l, op, r = self.__process_binop(arg)
                bin_op_str = "{0} {1} {2}".format(l, op, r)
                call_dict["params"].append(bin_op_str)
            elif isinstance(arg, ast.Str):
                str_message = "\"" + arg.s + "\""
                call_dict["params"].append(str_message)

    def visit_FunctionDef(self, node):
        """AST visitor in-built method, executed whenever a function def is encountered in AST tree visit.

        Returns None; must call self.generic_visit(node)"""

        self.count_hash["level"] += 1
        fdef_dict = self.program_dict["fdefs"]
        self.count_hash["fdefs"] += 1
        fdef_key = "fdef_{0}".format(self.count_hash["fdefs"])
        fdef_dict[fdef_key] = {}
        fdef_dict[fdef_key]["name"] = node.name

        fdef_dict[fdef_key]["retval"] = node.returns
        fdef_dict[fdef_key]["lineno"] = node.lineno
        fdef_dict[fdef_key]["level"] = self.count_hash["level"]
        fdef_dict[fdef_key]["args"] = []
        for arg in node.args.args:
            fdef_dict[fdef_key]["args"].append(arg.arg)
        fdef_dict[fdef_key]["body"] = {}
        
        body_dict = fdef_dict[fdef_key]["body"]
        fdef_dict = fdef_dict[fdef_key]
        self.fdef_key = fdef_key
        for cat in ["whiles", "fors", "ifs", "ops", "calls"]:
            self.program_dict["fdefs"][self.fdef_key]["num_{0}".format(cat)] = 0
        self.__process_body(node, body_dict)
        self.count_hash["level"] -= 1
        self.generic_visit(node)
