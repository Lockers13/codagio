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
    __node_types = ["fdefs", "whiles", "ifs", "fors", "assigns", "augassigns", "fcalls", "calls", "ops", "elses", "trys", "exc_handlers", "returns", "else-ifs", "withs"]

    def __init__(self, analyzer):
        # create glboal program dict [important!]
        self.__program_dict = analyzer.get_prog_dict()
        self.__stock_functions = ["main", "prep_input"]
        # create global hash map to keep count of occurrence of given types of nodes (see __parse_categories)
        self.__program_dict["count_hash"] = {}
        self.__count_hash = self.__program_dict["count_hash"]
        self.__program_dict["line_indents"] = {}
        self.__program_dict["nested_fdefs"] = []
        self.__nested_fdefs = self.__program_dict["nested_fdefs"]
        # get simple instance reference to count hash map
        self.__program_dict["nested_loops"] = []
        self.__nested_loops = self.__program_dict["nested_loops"]
        self.__program_dict["fdefs"] = {}
        # initialize sub dicts
        for n_type in self.__node_types:
            self.__count_hash[n_type] = 0
        # initialize count var to record indentation level [important!]
        self.__count_hash["level"] = -1
        # count var to record number of primitive operations (e.g. assign, aug_assign, etc.)
        self.__count_hash["nest_level"] = -1
        self.__metadata = analyzer.get_meta()
        self.__allowed_abs_imports = self.__metadata.get("constraints").get("allowed_abs_imports", [])
        self.__allowed_rel_imports = self.__metadata.get("constraints").get("allowed_rel_imports", {})
        self.__disallowed_fcalls = set(["exec", "eval", "open"]) ### !!! what about 'open'?
        for func in self.__metadata.get("constraints").get("disallowed_fcalls", []):
            self.__disallowed_fcalls.add(func)
        self.__num_args = int(self.__metadata.get("constraints").get("num_args", 0))
        self.__program_dict["constraint_violation"] = []
        self.__program_dict["udef_func_time_tot"] = 0
        self.__program_dict["imports"] = []

 
    def get_program_dict(self):
        return self.__program_dict

    def __increment_counts(self, node):
        node_type = type(node).__name__.lower()
        plural_id = "{0}s".format(node_type)
        self.__count_hash[plural_id] += 1
        self.__fdef_dict["{0}".format(plural_id)] += 1

    def __process_simple_op(self, node):
        self.__count_hash["ops"] += 1
        self.__fdef_dict["ops"] += 1

        op_type = type(node).__name__.lower()

        try:
            value = type(node.value).__name__.lower()
        except:
            value = ""

        if value != "" and isinstance(value, ast.Call):
            self.__increment_counts(node.value)
            self.__program_dict["line_indents"]["line_{0}".format(node.value.lineno)] = self.__count_hash["level"]

        self.__fdef_dict["skeleton"].append("{0}{1} {2}".format("    " * self.__count_hash["level"], op_type, value))
        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]
        
    def __process_orelse(self, node, orelse):
        if isinstance(orelse, ast.If):
            if isinstance(node, ast.If):
                elseif = True
                self.__count_hash["else-ifs"] += 1
                self.__fdef_dict["else-ifs"] += 1
                self.__count_hash["ifs"] -= 1
                self.__fdef_dict["ifs"] -= 1
            self.__increment_counts(orelse)
            self.__process_conditional(orelse, elseif)
        else:
            self.__count_hash["elses"] += 1
            self.__fdef_dict["elses"] += 1
            self.__fdef_dict["skeleton"].append("{0}{1}".format("    " * self.__count_hash["level"], "else:"))
            self.__program_dict["line_indents"]["line_{0}".format(orelse.lineno-1)] = self.__count_hash["level"]
            self.__process_body(orelse, in_else=True)

    def __process_conditional(self, node, elseif=False):

        node_type = type(node).__name__.lower()
        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]
        # try to record test type
        try:
            test_type = type(node.test).__name__.lower()
        except:
            test_type = None

        conditional_type = "elif" if elseif else "if"
        self.__fdef_dict["skeleton"].append("{0}{1} {2}:".format("    " * self.__count_hash["level"], conditional_type, test_type))
        self.__process_body(node)

        try:
            orelse = node.orelse[0]
            self.__process_orelse(node, orelse)
        except IndexError:
            pass

    def __process_with(self, node):
        context_expr = type(node.items[0].context_expr).__name__.lower()
        node_type = type(node).__name__.lower()
        self.__fdef_dict["skeleton"].append("{0}{1} {2}:".format("    " * self.__count_hash["level"], node_type, context_expr))
        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]

        self.__process_body(node)

    def __process_try(self, node):
        node_type = type(node).__name__.lower()
        self.__fdef_dict["skeleton"].append("{0}{1}:".format("    " * self.__count_hash["level"], node_type))
        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]

        if len(node.handlers) == 0:
            self.__process_body(node)
        else:
            for handler in node.handlers:
                self.__process_body(node)
                self.__count_hash["exc_handlers"] += 1
                self.__fdef_dict["skeleton"].append("{0}{1}:".format("    " * self.__count_hash["level"], type(handler).__name__.lower()))
                self.__process_body(handler)
                # for body in handler.body:
                #     self.__process_body(body)

    def __process_loop(self, node, nested=False):
        """Utility method to recursively process any 'while', 'for' or 'if' node encountered in a function def,
        where by 'process' we mean => write pertinent info to appropriate place in prog dict.
        Note: this helper method calls '__process_body()' for the purposes of exploiting 
        the intrinsically recursive nature of the AST tree.

        Returns None"""

        self.__count_hash["nest_level"] += 1
        # get type of node
        node_type = type(node).__name__.lower()

        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]

        # try to record test type
        try:
            test_type = type(node.test).__name__.lower()
        except:
            test_type = "loop"

        self.__fdef_dict["skeleton"].append("{0}{1} {2}:".format("    " * self.__count_hash["level"], node_type, test_type))

        # record whether nested or not (default => False)
        if self.__count_hash["nest_level"] > 0:
            nest_dict = {
                "type": node_type,
                "lineno": node.lineno,
                "fname": self.__fname,
                "nest_level": self.__count_hash["nest_level"]
            }
            self.__nested_loops.append(nest_dict)
       
        # process body of node
        self.__process_body(node)
        self.__count_hash["nest_level"] -= 1

    def __process_fdef(self, node):
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)
        signature = "def {0}({1}):".format(node.name, ', '.join(parameters))
        self.__fdef_dict["skeleton"].append("{0}{1}".format("    " * self.__count_hash["level"], signature))
        self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]
        self.__process_body(node)

    def __process_import(self, node):
        pass

    def __process_body(self, node, in_else=False):

        """Utility method to recursively process the body of any given AST construct containing a body. 
        At the highest level, we start by processing the body of function definitions, then the bodies 
        of any while/for/if, etc., nodes encountered therein, and so on and so forth, until we reach a node with no body, 
        in which case we simply write the name of the node ('type(node).__name__'), and some other basic info.,
        to our prog dict and return None.
        
        Returns None"""

        def do_body(body_node):
            
            try:
                self.__increment_counts(body_node)
            except:
                pass
            if isinstance(body_node, ast.While) or isinstance(body_node, ast.For):
                nested = True if isinstance(node, ast.While) or isinstance(node, ast.For) else False
                self.__process_loop(body_node, nested)
            elif isinstance(body_node, ast.If):
                self.__process_conditional(body_node)
                elseif = False
            elif isinstance(body_node, ast.With):
                self.__process_with(body_node)
            elif isinstance(body_node, ast.Import):
                self.__process_import(body_node)
            elif isinstance(body_node, ast.Expr):
                value = body_node.value
                if isinstance(value, ast.Call):
                    self.__increment_counts(value)
                    self.__program_dict["line_indents"]["line_{0}".format(value.lineno)] = self.__count_hash["level"]
                    func = value.func
                    try:
                        func_name = func.id
                    except AttributeError:
                        try:
                            func_name = func.attr
                        except:
                            func_name = ""
                else:
                    func_name = ""
                node_type = type(value).__name__.lower()
                self.__fdef_dict["skeleton"].append("{0}{1} to '{2}'".format("    " * self.__count_hash["level"], node_type, func_name))
            elif isinstance(body_node, ast.Try):
                self.__process_try(body_node)
            elif isinstance(body_node, ast.FunctionDef):
                self.__nested_fdefs.append(body_node.name)
                self.__process_fdef(body_node)
            else:
                self.__process_simple_op(body_node)

        # increment indentation level count before entering any node body
        self.__count_hash["level"] += 1
        # if there are multiple body elems, iterate through them; else process single body elem
        if in_else:
            do_body(node)
        else:
            try:
                for body_node in node.body:
                    do_body(body_node)
            except AttributeError as e:
                do_body(node)

        # decrement indentation level count upon exiting any node body            
        self.__count_hash["level"] -= 1

    def visit_FunctionDef(self, node, cls_method=False):
        """AST visitor in-built method, executed whenever a function def is encountered in AST tree visit.

        Returns None; must call self.generic_visit(node) as last statement"""
        
        if node.name not in self.__stock_functions:
            self.__count_hash["level"] += 1
            fdef_dict = self.__program_dict["fdefs"]
            self.__count_hash["fdefs"] += 1
            fdef_key = "fdef_{0}".format(self.__count_hash["fdefs"])
            self.__fname = node.name
            fdef_dict[fdef_key] = {}
            self.__fdef_dict = fdef_dict[fdef_key]
            self.__fdef_dict["name"] = node.name
            # self.__fdef_dict["retval"] = node.returns
            self.__fdef_dict["lineno"] = node.lineno
            # self.__fdef_dict["level"] = self.__count_hash["level"]
            self.__program_dict["line_indents"]["line_{0}".format(node.lineno)] = self.__count_hash["level"]
            self.__fdef_dict["args"] = []

            for arg in node.args.args:
                self.__fdef_dict["args"].append(arg.arg)
            num_args = len(self.__fdef_dict["args"])

            if self.__fname == self.__metadata.get("main_function") and num_args != self.__num_args:
                self.__program_dict["constraint_violation"].append({"num_args": "specification={0} - user-code={1}".format(self.__num_args, num_args)})

            signature = "def {0}({1}):".format(node.name, ', '.join(self.__fdef_dict["args"]))
            if self.__fname == self.__metadata.get("main_function"):
                self.__program_dict["main_signature"] = signature
            self.__fdef_dict["skeleton"] = []
            self.__fdef_dict["skeleton"].append(signature)
            for cat in ["whiles", "fors", "ifs", "ops", "calls", "elses", "assigns", "augassigns", "trys", "returns", "else-ifs", "withs"]:
                self.__fdef_dict["{0}".format(cat)] = 0
            self.__process_body(node)
            self.__count_hash["level"] -= 1

        self.generic_visit(node)

    def visit_Import(self, node):
        self.__program_dict["imports"].append("{0}".format("absolute import"))
        for imp in node.names:
            if imp.name not in self.__allowed_abs_imports:
               unsafe_entry_list = self.__program_dict["constraint_violation"]
               unsafe_entry_list.append({
                    "type": "Absolute import",
                    "name": imp.name
                })
                
    def visit_ImportFrom(self, node):
        self.__program_dict["imports"].append("{0}".format("relative import"))
        module = node.module
        rel_imps = self.__allowed_rel_imports.get(module, None)
        if rel_imps is None:
            unsafe_entry_list = self.__program_dict["constraint_violation"]
            unsafe_entry_list.append({
                "type": "Relative import",
                "name": "from {0}".format(module)
            })
        else:
            for imp in node.names:
                if imp.name not in rel_imps:
                    unsafe_entry_list = self.__program_dict["constraint_violation"]
                    unsafe_entry_list.append({
                        "type": "Relative import",
                        "name": imp.name
                    })

    def visit_Call(self, node):
        def check_safe_open(func_name, node):
            if func_name == "open":
                if len(node.args) == 2 and isinstance(node.args[0], ast.Name) and isinstance(node.args[1], ast.Str):
                    if node.args[0].id in self.__fdef_dict["args"] and node.args[1].s == 'r':
                        return True
            return False

        try:
            func_name = node.func.id
        except AttributeError:
            try:
                func_name = node.func.attr
            except:
                func_name = node.func.slice
        
        if func_name in self.__disallowed_fcalls:
            if check_safe_open(func_name, node):
                pass
            else:
                unsafe_entry_list = self.__program_dict["constraint_violation"]
                unsafe_entry_list.append({
                    "type": "Disallowed fcall",
                    "name": func_name
                })
        
    def auto_validate(self):
        """Function to check if any violations have been recorded during ast_analysis
        
        Returns appropriate http reponse if any violations are found, true otherwise"""

        # check to see if ast visitor encountered any constraint violations
        constraints_vlen = len(self.__program_dict["constraint_violation"])
        if constraints_vlen > 0:
            print("POST NOT OK: constraint violation(s) : {0}" .format(self.__program_dict["constraint_violation"]))
            return False
        return True
