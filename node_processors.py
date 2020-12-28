import ast

bin_ops = {"Add": '+', "Sub": '-', "Mult": '*', "Div": '/', "FloorDiv": "//",
           "Mod": '%', "Pow": "**", "LShift": "<<", "RShift": ">>",
           "BitOr": '|', "BitXor": '^', "BitAnd": '&', "MatMult": '@', "Lt": '<', "Gt": '>'}

def process_test(test, test_dict):
    test_dict[type(test).__name__.lower()] = ""
    
    #     try:
    #         val_iter = iter(v)
    #         test_dict[k] = []
    #         for vv in val_iter:
    #             if isinstance(vv, ast.Name):
    #                 test_dict[k].append(vv.id)
    #             else:
    #                 test_dict[k].append(bin_ops[type(vv).__name__])
    #     except:
    #         if isinstance(v, ast.Name):
    #             test_dict[k] = v.id
    #         elif isinstance(v, ast.Subscript):
    #             test_dict[k] = "{0}[{1}]".format(str(v.value.id), v.slice.value.id)
    # test_dict["brute_fields"] = tdict

    # global bin_ops
    # test_vars = vars(test)
    # for key in test_vars.keys():
    #     try:
    #         iter_obj = test_vars[key]
    #         test_dict[key] = []
    #         for i in iter_obj:
    #             test_dict[key].append(i.values())
    #     except:
    #         obj = test_vars[key]
    #         test_dict[key] = obj
        # try:
        #     obj = test_vars[key][0]
        #     if isinstance(obj, ast.Name):
        #         if key == "comparators":
        #             test_dict["comp"] = vars(obj)
        #     else:
        #         test_dict["ops"] = bin_ops[type(obj).__name__]
        # except:
        #     if isinstance(test_vars[key], ast.Name):
        #         if key == "left":
        #             test_dict["left"] = test_vars[key].id

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
    node_dict["for"]["body"] = {}
    for i in node.body:
        for k,v in vars(i).items():
            if isinstance(v, ast.Call):
                node_dict["for"]["body"]["func"] = {}
                for_call = node_dict["for"]["body"]["func"]
                process_call(v, for_call)
            else:
                node_dict["for"]["body"][k] = v

def process_while(node, node_dict):
    while_id = "{0}_{1}".format(type(node).__name__, node.lineno)
    node_dict[while_id] = {}
    process_test(node.test, node_dict[while_id]["test"])
    node_dict[while_id]["body"] = {}
    

def process_targets(node, node_dict):
    targ_list = []
    node_dict["type"] = type(node).__name__
    try:
        for i in node:
            if isinstance(i, ast.Tuple):
                node_dict["vals"] = {}
                node_vars = vars(i)
                for k, v in node_vars.items():
                    try:
                        iter(v)
                        node_dict["vals"][k] = process_simple_obj(v, iterable=True)
                    except:
                        node_dict["vals"][k] = process_simple_obj(v)

            else:
                targ_list.append(process_simple_obj(i))
                node_dict["targs"] = targ_list
    except Exception as e:
        node_dict["err"] = str(e)

def process_simple_obj(obj, iterable=False):
    if iterable:
        val_list = []
        for i in obj:
            print(i)
            val_list.append(process_simple_obj(i))
        return val_list
    else:
        if isinstance(obj, ast.Name):
            return obj.id
        elif isinstance(obj, ast.Subscript):
            return "{0}[{1}]".format(str(obj.value.id), obj.slice.value.id)
        else:
            return obj

def process_value(node, node_dict):
    try:
        (node.func)
        if isinstance(node.func, ast.Name):
            node_dict["fname"] = node.func.id
            node_dict["lineno"] = node.func.lineno
        else:
            node_dict["fname"] = node.func.attr
            node_dict["lineno"] = node.func.lineno
    except:
        if isinstance(node, ast.Tuple):
            node_dict["vals"] = {}
            node_vars = vars(node)
            for k, v in node_vars.items():
                try:
                    iter(v)
                    node_dict["vals"][k] = process_simple_obj(v, iterable=True)
                except:
                    node_dict["vals"][k] = process_simple_obj(v)

def process_try(node, node_dict):
    node_dict["try"] = {}
    node_dict["try"]["body"] = {}
    node_dict["try"]["body"]["type"] = {}
    for i in node.body:
        for k,v in vars(i).items():
            node_dict["try"]["body"][k] = v
    node_dict["try"]["handler"] = vars(node)

def process_assign(node, node_dict):
    node_dict["assign"] = {}
    node_dict["assign"]["targets"] = {}
    count = 0
    target_dict = node_dict["assign"]["targets"]
    process_targets(node.targets, target_dict)

    node_dict["assign"]["value"] = {}
    process_value(node.value, node_dict["assign"]["value"])



def process_if(node, node_dict):
    node_dict["if"] = {}
    node_dict["if"]["test"] = {}
    node_dict["if"]["body"] = {}
    iftest_dict = node_dict["if"]["test"]
    inner_body_dict = node_dict["if"]["body"]
    process_test(node.test, iftest_dict)
    for i in node.body:
        process_body(i, inner_body_dict)

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

processor_funcs = {"For": process_for, "While": process_while, "If": process_if, "Assign": process_assign,
                   "Try": process_try, "With": process_with, "AugAssign": process_aug_assign, "Call": process_call}

def process_body(node, node_dict):
    node_name = type(node).__name__
    if node_name in processor_funcs.keys():
        processor_funcs[node_name](node, node_dict)
