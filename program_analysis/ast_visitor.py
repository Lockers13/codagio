import ast

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
    __node_types = ["fdefs", "whiles", "ifs", "fors", "assigns", "augassigns", "fcalls", "calls", "ops", "elses", "trys", "exc_handlers", "returns"]

    # binary operation hash map, needed for translating AST's binop objects to more readable form
    # see '__process_binop()' below for usage
    __bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

    def __init__(self, analyzer):
        # create glboal program dict [important!]
        self.__program_dict = analyzer._program_dict
        # create global hash map to keep count of occurrence of given types of nodes (see __parse_categories)
        self.__program_dict["count_hash"] = {}
        # get simple instance reference to count hash map
        self.__count_hash = self.__program_dict["count_hash"]
        self.__program_dict["nested_loops"] = []
        self.__nested_loops = self.__program_dict["nested_loops"]
        self.__program_dict["fdefs"] = {}
        # initialize sub dicts
        for n_type in self.__node_types:
            self.__count_hash[n_type] = 0
        # initialize count var to record indentation level [important!]
        self.__count_hash["level"] = 0
        # count var to record number of primitive operations (e.g. assign, aug_assign, etc.)
        self.__count_hash["nest_level"] = -1
        self.__fname = None
        self.__reverse_class_dict = {}
        self.__program_dict["nested_fdefs"] = {}
        self.__nested_fdefs = self.__program_dict["nested_fdefs"]
    
    def get_program_dict(self):
        return self.__program_dict

    def __increment_counts(self, node):
        node_type = type(node).__name__.lower()
        pl_id = "{0}s".format(node_type)
        self.__count_hash[pl_id] += 1
        self.__program_dict["fdefs"][self.fdef_key]["num_{0}".format(pl_id)] += 1


    def __prep_body_dict(self, node, node_dict, count_key):
        """Utility method to initialize body_dict.

        Returns initialized body dict for specified node"""

        # create unique identifier key for any given node
        identifier = "{0}_{1}".format(type(node).__name__.lower(), self.__count_hash[count_key])
        node_dict[identifier] = {}
        node_dict[identifier]["lineno"] = node.lineno
        node_dict[identifier]["level"] = self.__count_hash["level"]
        node_dict[identifier]["body"] = {}
        return identifier, node_dict[identifier]["body"]

    def __process_simple_op(self, node, node_dict):
        self.__count_hash["ops"] += 1
        self.__program_dict["fdefs"][self.fdef_key]["num_ops"] += 1
        op_key = "op_{0}".format(self.__count_hash["ops"])
        node_dict[op_key] = {}
        
        op_type = type(node).__name__.lower()

        try:
            value = type(node.value).__name__.lower()
            if isinstance(value, ast.Call):
                self.__process_call(value, node_dict)
        except:
            value = None

        node_dict[op_key] = {
                "value": value,
                "type": op_type,
                "lineno": node.lineno,
                "level": self.__count_hash["level"]
        }
        
    def __process_conditional(self, node, node_dict, elseif=False):
        node_type = type(node).__name__.lower()
        cond_id = "if_{0}".format(self.__count_hash["ifs"])
        _, body_dict = self.__prep_body_dict(node, node_dict, "{0}s".format(node_type))
        # try to record test type
        try:
            node_dict[cond_id]["test_type"] = type(node.test).__name__.lower()
        except:
            pass

        node_dict[cond_id]["elif"] = elseif

        self.__process_body(node, body_dict)
        
        try:
            if isinstance(node.orelse[0], ast.If):
                if isinstance(node, ast.If):
                    elseif = True
                self.__count_hash["ifs"] += 1
                self.__program_dict["fdefs"][self.fdef_key]["num_ifs"] += 1
                self.__process_conditional(node.orelse[0], node_dict, elseif)
            else:
                self.__count_hash["elses"] += 1
                self.__program_dict["fdefs"][self.fdef_key]["num_elses"] += 1
                node_dict["else_{0}".format(self.__count_hash["elses"])] = {}
                else_dict = node_dict["else_{0}".format(self.__count_hash["elses"])]
                else_dict["level"] = self.__count_hash["level"]
                for body_node in node.orelse:
                    if isinstance(body_node, ast.If):
                        self.__process_conditional(body_node, else_dict)
                    else:
                        self.__process_body(body_node, else_dict)
        except Exception as e:
            pass

    def __process_try(self, node, node_dict):
        node_type = type(node).__name__.lower()
        _, body_dict = self.__prep_body_dict(node, node_dict, "{0}s".format(node_type))
        self.__process_body(node, body_dict)

        for handler in node.handlers:
            self.__count_hash["exc_handlers"] += 1
            node_dict["exc_handler_{0}".format(self.__count_hash["exc_handlers"])] = {}
            except_dict = node_dict["exc_handler_{0}".format(self.__count_hash["exc_handlers"])]

            for body in handler.body:
                self.__process_body(body, except_dict)

    def __process_loop(self, node, node_dict, nested=False):
        """Utility method to recursively process any 'while', 'for' or 'if' node encountered in a function def,
        where by 'process' we mean => write pertinent info to appropriate place in prog dict.
        Note: this helper method calls '__process_body()' for the purposes of exploiting 
        the intrinsically recursive nature of the AST tree.

        Returns None"""

        self.__count_hash["nest_level"] += 1
        # get type of node
        node_type = type(node).__name__.lower()
        # get body dict for node
        identifier, body_dict = self.__prep_body_dict(node, node_dict, "{0}s".format(node_type))
  
        # try to record test type
        try:
            body_dict["test_type"] = type(node.test).__name__.lower()
        except:
            pass
        # record whether nested or not (default => False)
        node_dict[identifier]["nested"] = nested
        node_dict[identifier]["nest_level"] = self.__count_hash["nest_level"]
        if self.__count_hash["nest_level"] > 0:
            nest_dict = {
                "type": node_type,
                "lineno": node.lineno,
                "fname": self.__fname,
                "nest_level": self.__count_hash["nest_level"]
            }
            self.__nested_loops.append(nest_dict)
       
        # process body of node
        self.__process_body(node, body_dict)
        self.__count_hash["nest_level"] -= 1
    
    def __process_body(self, node, node_dict):

        """Utility method to recursively process the body of any given AST construct containing a body. 
        At the highest level, we start by processing the body of function definitions, then the bodies 
        of any while/for/if, etc., nodes encountered therein, and so on and so forth, until we reach a node with no body, 
        in which case we simply write the name of the node ('type(node).__name__'), and some other basic info.,
        to our prog dict and return None.
        
        Returns None"""

        def do_body(body_node, node_dict):
            try:
                self.__increment_counts(body_node)
            except Exception as e:
                pass
            if isinstance(body_node, ast.While) or isinstance(body_node, ast.For):
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_loop(body_node, node_dict, nested)
            elif isinstance(body_node, ast.If):
                self.__process_conditional(body_node, node_dict)
                elseif = False
            elif isinstance(body_node, ast.Expr):
                if isinstance(body_node.value, ast.Call):
                    self.__process_call(body_node.value, node_dict)
                else:
                    node_dict["expr"] = type(body_node.value).__name__
            elif isinstance(body_node, ast.Try):
                self.__process_try(body_node, node_dict)
            elif isinstance(body_node, ast.FunctionDef):
                self.__nested_fdefs[self.__fname].append(body_node.name)
            else:
                self.__process_simple_op(body_node, node_dict)

        # increment indentation level count before entering any node body
        self.__count_hash["level"] += 1
        # if there are multiple body elems, iterate through them; else process single body elem
        try:
            for body_node in node.body:
                do_body(body_node, node_dict)
        except AttributeError:
            do_body(node, node_dict)

        # decrement indentation level count upon exiting any node body            
        self.__count_hash["level"] -= 1

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

        self.__increment_counts(node)
        call_key = "fcall_{0}".format(self.__count_hash["fcalls"])
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
                arg_func = "arg_func_{0}".format(self.__count_hash["fcalls"])
                call_dict[arg_func] = {}
                self.__process_call(arg, call_dict[arg_func], "{0}".format(self.__count_hash["fcalls"]))
            elif isinstance(arg, ast.BinOp):
                l, op, r = self.__process_binop(arg)
                bin_op_str = "{0} {1} {2}".format(l, op, r)
                call_dict["params"].append(bin_op_str)
            elif isinstance(arg, ast.Str):
                str_message = "\"" + arg.s + "\""
                call_dict["params"].append(str_message)

    def visit_FunctionDef(self, node, cls_method=False):
        """AST visitor in-built method, executed whenever a function def is encountered in AST tree visit.

        Returns None; must call self.generic_visit(node) as last statement"""
        

        self.__count_hash["level"] += 1
        fdef_dict = self.__program_dict["fdefs"]
        self.__count_hash["fdefs"] += 1
        fdef_key = "fdef_{0}".format(self.__count_hash["fdefs"])
        fdef_dict[fdef_key] = {}
        fdef_dict[fdef_key]["name"] = node.name
        
        if self.__reverse_class_dict.get(node.name):
            cls_method = True
            parent_class = self.__reverse_class_dict.get(node.name)
            self.__count_hash["level"] += 1
        else:
            parent_class = None
            if self.__count_hash["level"] > 0:
                self.__count_hash["level"] -= 1

        fdef_dict[fdef_key]["class_method"] = cls_method
        fdef_dict[fdef_key]["parent_class"] = parent_class
        fdef_dict[fdef_key]["retval"] = node.returns
        fdef_dict[fdef_key]["lineno"] = node.lineno
        fdef_dict[fdef_key]["level"] = self.__count_hash["level"]
        fdef_dict[fdef_key]["args"] = []
        for arg in node.args.args:
            fdef_dict[fdef_key]["args"].append(arg.arg)
        fdef_dict[fdef_key]["body"] = {}

        body_dict = fdef_dict[fdef_key]["body"]
        fdef_dict = fdef_dict[fdef_key]
        self.fdef_key = fdef_key
        self.__fname = node.name
        self.__nested_fdefs[self.__fname] = []
        for cat in ["whiles", "fors", "ifs", "ops", "calls", "elses", "assigns", "augassigns", "trys", "returns"]:
            self.__program_dict["fdefs"][self.fdef_key]["num_{0}".format(cat)] = 0
        self.__process_body(node, body_dict)
        self.__count_hash["level"] -= 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
        for m in node.body:
            if isinstance(m, ast.FunctionDef):
                self.__reverse_class_dict[m.name] = node.name
        self.generic_visit(node)