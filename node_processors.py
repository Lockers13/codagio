import ast

bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

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

def process_call(call_node, fcd):
    call_node_str = str(call_node)
    fcd[call_node_str] = {}
    if isinstance(call_node.func, ast.Name):
        fcd[call_node_str]["name"] = call_node.func.id
        fcd[call_node_str]["lineno"] = call_node.func.lineno
    else:
        fcd[call_node_str]["name"] = call_node.func.attr
        fcd[call_node_str]["lineno"] = call_node.func.lineno

def process_for(node, node_dict):
    node_dict["for"] = {}
    node_dict["for"]["iter"] = vars(node.iter)
    node_dict["for"]["target"] = vars(node.target)

def process_while(node, node_dict):
    node_dict["while"] = {}
    node_dict["while"]["test"] = []
    node_dict["while"]["test"].append(vars(node.test))
    node_dict["while"]["body"] = {}
    inner_body_dict = node_dict["while"]["body"]
    for i in node.body:
        process_body(i, inner_body_dict)

def process_try(node, node_dict):
    node_dict["try"] = {}
    node_dict["try"]["body"] = {}
    node_dict["try"]["body"]["type"] = {}
    for i in node.body:
        for k,v in vars(i).items():
            node_dict["try"]["body"][k] = v
    node_dict["try"]["handler"] = vars(node)

def process_if(node, node_dict):
    node_dict["if"] = {}
    node_dict["if"]["test"] = {}
    if_dict = node_dict["if"]["test"]
    process_test(node.test, if_dict)

def process_with(node, node_dict):
    node_dict["with"] = {}
    node_dict["with"]["items"] = {}
    for withitem in node.items:
        for k, v in vars(withitem.context_expr).items():
            try:
                node_dict["with"]["items"][k] = vars(v)
            except:
                pass

def process_aug_assign(node, node_dict):
    node_dict["aug_assign"] = {}
    for k, v in vars(node).items():
        try:
            node_dict["aug_assign"][k] = vars(v)
        except:
            node_dict["aug_assign"][k] = v

processor_funcs = {"For": process_for, "While": process_while, "If": process_if,
                   "Try": process_try, "With": process_with, "AugAssign": process_aug_assign}

def process_body(node, node_dict):
    node_name = type(node).__name__
    if node_name in processor_funcs.keys():
        processor_funcs[node_name](node, node_dict)
