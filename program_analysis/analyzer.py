import ast
import argparse
from ast_visitor import AstTreeVisitor
from prog_profiler import Profiler
from output_verifier import Verifier
import json
import sys
import os

# example submission call : python analyzer.py -s prime_checker -t submission -l
# example sample call : python analyzer.py -s quicksort -t sample -l

def parse_clargs():
    """Helper function to parse command line args.

    Returns arg dict"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--script", type=str, required=True,
                help="name of script to be analyzed")
    ap.add_argument("-t", "--type", type=str, required=True,
                help="submission or sample") 
    ap.add_argument("-g", action="store_true")
    ap.add_argument("-l", action="store_true")
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
    upload_type = "submissions" if args.get("type") == "submission" else "sample_problems" if args.get("type") == "sample" else None

    if upload_type is None:
        sys.exit(1)

    # script to be analyzed
    try:
        filename = os.path.join(upload_type, args.get("script"), "{0}.py".format(args.get("script")))  
    except:
        print("Error: incorrect clargs!")
        sys.exit(1)
    
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

    verifier = Verifier(filename)
    score = verifier.verify_output()

    profiler.profile(args)
    prog_dict["score"] = score

    # write prog_dict to disk in json format
    with open("{0}_analysis.json".format(filename.split(".")[0]), 'w') as f:
        f.write(json.dumps(prog_dict))
    # recursively print prog dict using helper function defined above
    rprint_dict(prog_dict)


main()
