import ast
import json
import sys
import os
from .ast_visitor import AstTreeVisitor
from .profiling import Profiler
from .verification import Verifier

class Analyzer:

    def __init__(self, filename, metadata):
        self.__program_dict = {}
        self.__filename = filename
        self.__metadata = metadata

    def get_prog_dict(self):
        return self.__program_dict
    
    def get_meta(self):
        return self.__metadata
    
    def get_filename(self):
        return self.__filename

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
        try:
            parsed_tree = ast.parse((open(self.__filename)).read())
        except Exception as e:
            raise Exception(str(e))
        # initialise ast tree visitor instance
        atv = AstTreeVisitor(self)
        # visit ast-parsed script
        atv.visit(parsed_tree)
        return atv.auto_validate()
    
    def verify(self, paragon):
        verifier = Verifier(self, paragon)
        return verifier.verify_output()

    def profile(self, inputs, solution=True, init_data=None):
        profiler = Profiler(self, inputs, init_data=init_data)
        
        profiler.cprof()

        if solution:
            profiler.lprof()

        #profiler.gnu_time_stats()

