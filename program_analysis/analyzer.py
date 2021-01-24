import ast
import json
import sys
import os
from ast_visitor import AstTreeVisitor
from profiling import Profiler
from verification import Verifier
from comparison import Comparer

class Analyzer:

    def __init__(self, filename, args):
        self.__program_dict = {}
        self.__filename = filename
        self.__simple_basename = os.path.basename(self.__filename).split(".")[0]
        self.__data_path = os.path.join("sample_problems", self.__simple_basename, self.__simple_basename)
        self.__args = args
    
    def get_prog_dict(self):
        return self.__program_dict
    
    def get_args(self):
        return self.__args
    
    def get_paths(self):
        return self.__filename, self.__simple_basename, self.__data_path

    def rprint_dict(self, nested, indent=0):
        """Helper function to recursively print nested program_dict.

        Returns None"""

        for k, v in nested.items():
            if isinstance(v, dict):
                print("{0}{1}:".format("    " * indent, k))
                self.rprint_dict(v, indent+1)
            else:
                print("{0}{1}: {2}".format("    " * indent, k, v))
    
    def write_to_json(self):
        with open("{0}_analysis.json".format(self.__filename.split(".")[0]), 'w') as f:
            f.write(json.dumps(self.get_prog_dict()))
    
    def visit_ast(self):
        parsed_tree = ast.parse((open(self.__filename)).read())
        # initialise ast tree visitor instance
        atv = AstTreeVisitor(self)
        # visit ast-parsed script
        atv.visit(parsed_tree)
    
    def verify(self):
        verifier = Verifier(self)
        verifier.verify_output()

    def profile(self):
        profiler = Profiler(self)
        
        ### Note : cprof must be called before lprof as the latter's results depend on the former's 
        ### ^ This needs to be fixed for multiprocessing purposes

        profiler.cprof()

        if self.__args.get("l") or self.__args.get("type") == "sample":
            profiler.lprof()
        if self.__args.get("g"):
            profiler.gnu_time_stats()

    def compare(self):
        comparer = Comparer(self)
        return comparer.compare()
