import os
from rest_framework.response import Response
from rest_framework import status

def validate(ast_analysis, filename):
    os.remove(filename)
    num_fdefs = len(ast_analysis["fdefs"].keys())
    constraints_vlen = len(ast_analysis["constraint_violation"])
    if num_fdefs != 1:
        return Response("POST NOT OK: Too few or too many function(s) => {0}".format(num_fdefs), status=status.HTTP_400_BAD_REQUEST)
    # see if ast visitor found any constraint violations
    if constraints_vlen > 0:
        return Response("POST NOT OK: contraint violation(s) : {0}" .format(ast_analysis["constraint_violation"]), status=status.HTTP_400_BAD_REQUEST)
    ### remove old basic file and create more sophisticated one for verification and profiling
    return True
