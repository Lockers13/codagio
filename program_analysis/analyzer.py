import ast
import argparse
from ast_visitor import AstTreeVisitor
from prog_profiler import Profiler
import json

def parse_clargs():
    """Helper function to parse command line args.

    Returns arg dict"""

    ap = argparse.ArgumentParser() 
    ap.add_argument("-g", action="store_true")
    return vars(ap.parse_args())

def rprint_dict(nested, indent=0):
    """Helper function to recursively print nested dicts.

    Returns None"""

    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))

def main():
    # get arg dict
    args = parse_clargs()
    # script to be parsed
    filename = "quicksort.py"
    # parse script using AST module
    parsed_tree = ast.parse((open(filename)).read())
    # initialise ast tree visitor instance
    ast_visitor = AstTreeVisitor()
    # visit ast-parsed script
    ast_visitor.visit(parsed_tree)
    # get populated prog_dict
    prog_dict = ast_visitor.get_program_dict()
    # print(ast_visitor.count_hash)
    # initialise profiler instance, passing original script name and prog_dict for further writing of profiling info
    profiler = Profiler(filename, prog_dict)

    #profiler.profile(args)

    # write prog_dict to disk in json format
    with open("analysis.json", 'w') as f:
        f.write(json.dumps(prog_dict))
    # recursively print prog dict using helper function defined above
    rprint_dict(prog_dict)

main()