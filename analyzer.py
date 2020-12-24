import ast
import argparse
from ast_visitor import AstTreeVisitor
from prog_profiler import Profiler

def parse_clargs():
    ap = argparse.ArgumentParser() 
    ap.add_argument("-m", action="store_true")
    return vars(ap.parse_args())

def rprint_dict(nested, indent=0):
    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))

args = parse_clargs()
# filename = input(str("Please enter the name of a file to parse: "))
filename = "quicksort.py"
parsed_tree = ast.parse((open(filename)).read())

ast_visitor = AstTreeVisitor()
ast_visitor.visit(parsed_tree)

profiler = Profiler(filename, ast_visitor.program_dict)
profiler.profile()

rprint_dict(ast_visitor.program_dict)