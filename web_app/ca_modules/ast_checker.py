import os
from rest_framework.response import Response
from rest_framework import status

def validate(ast_analysis, filename):
    if len(ast_analysis["fdefs"].keys()) != 1:
        os.remove(filename)
        return Response("POST NOT OK: more or less than 1 function!", status=status.HTTP_400_BAD_REQUEST)
    # see if ast visitor found any constraint violations
    if len(ast_analysis["constraint_violation"]) > 0:
        os.remove(filename)
        return Response("POST NOT OK: contraint violation(s) : {0}" .format(ast_analysis["constraint_violation"]), status=status.HTTP_400_BAD_REQUEST)
    ### remove old basic file and create more sophisticated one for verification and profiling
    os.remove(filename)
    return True
