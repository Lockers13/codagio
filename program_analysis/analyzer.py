import ast
from ast_visitor import AstTreeVisitor
from prog_profiler import Profiler
from output_verifier import Verifier
import json
import sys
import os

class Analyzer:
    def __init__(self, filename, args):
        self._program_dict = {}
        self._filename = filename
        self._simple_basename = os.path.basename(self._filename).split(".")[0]
        self._data_path = self.__data_path = os.path.join("sample_problems", self._simple_basename, self._simple_basename)
        self._args = args

    def get_prog_dict(self):
        return self._program_dict

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
        with open("{0}_analysis.json".format(self._filename.split(".")[0]), 'w') as f:
            f.write(json.dumps(self.get_prog_dict()))
    
    def visit_ast(self):
        parsed_tree = ast.parse((open(self._filename)).read())
        # initialise ast tree visitor instance
        atv = AstTreeVisitor(self)
        # visit ast-parsed script
        atv.visit(parsed_tree)
    
    def verify(self):
        verifier = Verifier(self)
        verifier.verify_output()

    def profile(self):
        profiler = Profiler(self)
        profiler.profile(self._args)