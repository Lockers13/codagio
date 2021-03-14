import ast

def show_function_details(script):
    function_details_list = []
    with open(script, 'r') as f:
        parsed_ast = ast.parse(f.read())
    functions = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
    for func in functions:
        params = []
        func_name = func.name
        visibility = "private" if func_name.startswith("_") else "public"
        for arg in func.args.args:
            params.append(arg.arg)
        fd_item = "{0}:{1}:{2}".format(func_name, visibility, ",".join(params))
        if fd_item not in function_details_list:
            function_details_list.append(fd_item)
    for function_details in sorted(function_details_list, key=str.lower):
        print(function_details)
