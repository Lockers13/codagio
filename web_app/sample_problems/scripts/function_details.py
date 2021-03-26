import ast

def show_function_details(script):
    function_details = {}
    with open(script, 'r') as f:
        parsed_ast = ast.parse(f.read())
    functions = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
    for func in functions:
        params = []
        func_name = func.name
        visibility = "private" if func_name.startswith("_") else "public"
        for arg in func.args.args:
            params.append(arg.arg)
        function_info = "{0} - {1} - {2}".format(func_name, visibility, ",".join(params))
        function_details[func.lineno] = function_info
    return function_details