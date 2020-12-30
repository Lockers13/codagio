import ast
from collections import OrderedDict

### Note: remember to catch elifs, elses, etc....'node.orelse'

class AstTreeVisitor(ast.NodeVisitor):
    """Class for visiting AST tree. We vist only function definitions, adding each entry to our global program dict,
    and then we process the bodies of the function definitions using helper functions in order to preserve scope context.
    We repeat this proedure recursively for all nodes in the body of th function def, and so on until we arrive at a node having no body,
    which is essentially our base case.
    
    Note: we assume that all code in the provided script (except for the calling of the 'main()' routine) is 
    enclosed within a function defintion of some sort; so, for example, a sample script provided to our AST parser 
    might look like: the following:

    import ...

    def f(x):
        def g(x):
            some code...
        more code...
    
    def h(x):
        further code...
    
    def main():
        if h(a):
            f(b)
        else:
            h(c)
    
    main()

    """

    # private instance var determining what entries to initialize in global program dict
    __parse_categories = ["modules", "fdefs", "fcalls", "whiles", "ifs", "fors", "assigns", "aug_assigns", "calls"]

    # binary operation hash map, needed for translating AST's binop objects to more readable form
    # see '__process_binop()' below for usage
    __bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

    def __init__(self):
        # create glboal program dict [important!]
        self.program_dict = OrderedDict()
        # create global hash map to keep count of occurrence of given types of nodes (see __parse_categories)
        self.program_dict["count_hash"] = {}
        # get simple instance reference to count hash map
        self.count_hash = self.program_dict["count_hash"]
        # initialize sub dicts
        for pcat in self.__parse_categories:
            self.program_dict[pcat] = OrderedDict()
            self.count_hash[pcat] = 0
        # initialize count var to record indentation level [important!]
        self.count_hash["level"] = -1
        # count var to record number of primitive operations (e.g. assign, aug_assign, etc.)
        self.count_hash["ops"] = 0
        self.count_hash["elses"] = 0
        self.fname = None
    
    def __prep_body_dict(self, node, node_dict, count_key):
        """Utility method to initialize body_dict.

        Returns initialized body dict for specified node"""

        # create unique identifier key for any given node
        identifier = "{0}_{1}".format(type(node).__name__.lower(), self.count_hash[count_key])
        node_dict[identifier] = OrderedDict()
        node_dict[identifier]["lineno"] = node.lineno
        node_dict[identifier]["level"] = self.count_hash["level"]
        node_dict[identifier]["body"] = {}
        return node_dict[identifier]["body"]

    def __process_conditional(self, node, node_dict, elseif=False):
        # get type of node
        node_type = type(node).__name__.lower()
        cond_id = "if_{0}".format(self.count_hash["ifs"])
        # get body dict for node
        body_dict = self.__prep_body_dict(node, node_dict, "{0}s".format(node_type))
        # try to record test type
        try:
            node_dict[cond_id]["test_type"] = type(node.test).__name__.lower()
        except:
            pass

        node_dict[cond_id]["elif"] = elseif

        # check for occurrence of else clauses
        if any(not isinstance(cond, ast.If) for cond in node.orelse):
            self.count_hash["elses"] += 1
            self.program_dict["fdefs"][self.fdef_key]["num_elses"] += 1
            node_dict["else_{0}".format(self.count_hash["elses"])] = {}
            else_dict = node_dict["else_{0}".format(self.count_hash["elses"])]
            else_dict["level"] = self.count_hash["level"]

        # process body of node
        self.__process_body(node, body_dict)

        ### Todo: functionalize simple op processing, e.g. => __process_op ###
        else_subcount = 0
        for cond_or_op in node.orelse:
            if isinstance(cond_or_op, ast.If):
                self.count_hash["ifs"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_ifs"] += 1
                self.__process_conditional(cond_or_op, node_dict, elseif=True)
            else:
                else_subcount += 1
                if else_subcount == 1:
                    else_dict["lineno"] = cond_or_op.lineno - 1
                self.count_hash["ops"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_ops"] += 1
                elsop_key = "op_{0}".format(self.count_hash["ops"])
                else_dict[elsop_key] = {}
                try:
                    value = cond_or_op.value
                    if isinstance(value, ast.Call):
                        self.__process_call(valie, else_dict)
                    else_dict[elsop_key]["value"] = type(value).__name__.lower()
                except:
                    value = vars(cond_or_op)
                    else_dict[elsop_key]["value"] = value
                else_dict[elsop_key] = {
                    "type": type(cond_or_op).__name__.lower(),
                    "lineno": cond_or_op.lineno,
                    "level": self.count_hash["level"]
                }
        
    def __process_loop(self, node, node_dict, nested=False):
        """Utility method to recursively process any 'while', 'for' or 'if' node encountered in a function def,
        where by 'process' we mean => write pertinent info to appropriate place in prog dict.
        Note: this helper method calls '__process_body()' for the purposes of exploiting 
        the intrinsically recursive nature of the AST tree.

        Returns None"""

        # get type of node
        node_type = type(node).__name__.lower()
        # get body dict for node
        body_dict = self.__prep_body_dict(node, node_dict, "{0}s".format(node_type))
        # try to record test type
        try:
            body_dict["test_type"] = type(node.test).__name__.lower()
        except:
            pass
        # record whether nested or not (default => False)
        body_dict["nested"] = nested
        # process body of node
        self.__process_body(node, body_dict)

    def __process_body(self, node, node_dict):
        """Utility method to recursively process the body of any given AST construct containing a body. 
        At the highest level, we start by processing the body of function definitions, then the bodies 
        of any while/for/if, etc., nodes encountered therein, and so on and so forth, until we reach a node with no body, 
        in which case we simply write the name of the node ('type(node).__name__'), and some other basic info.,
        to our prog dict and return None.
        
        Returns None"""

        # increment indentation level count before entering any node body
        self.count_hash["level"] += 1

        for body_node in node.body:
            if isinstance(body_node, ast.While) or isinstance(body_node, ast.For):
                body_node_type = type(body_node).__name__.lower()
                self.count_hash["{0}s".format(body_node_type)] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_{0}s".format(body_node_type)] += 1
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_loop(body_node, node_dict, nested)
            elif isinstance(body_node, ast.If):
                self.count_hash["ifs"] += 1
                self.program_dict["fdefs"][self.fdef_key]["num_ifs"] += 1
                self.__process_conditional(body_node, node_dict)
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
        # decrement indentation level count upon exiting any node body            
        self.count_hash["level"] -= 1

    def __process_binop(self, arg):
        """Utility method to make AST BinOp constructs more readable.

        Returns binop_list => e.g. ['a', '**', '2']"""

        binop_list = []
        # range(3) => lhs, op, rhs
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
        """Utility method to recursively process any 'call' constructs encountered in AST fdefs.

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

        Returns None; must call self.generic_visit(node) as last statement"""

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
        for cat in ["whiles", "fors", "ifs", "ops", "calls", "elses"]:
            self.program_dict["fdefs"][self.fdef_key]["num_{0}".format(cat)] = 0
        self.__process_body(node, body_dict)
        self.count_hash["level"] -= 1
        self.generic_visit(node)