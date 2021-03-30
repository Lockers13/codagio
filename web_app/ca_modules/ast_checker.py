import os
from rest_framework.response import Response
from rest_framework import status

def validate(ast_analysis, filename):
    """Function to check if any violations have been recorded during ast_analysis
    
    Returns appropriate http reponse if any violations are found, true otherwise"""

    ### first off, remove the old basic file that was used for initial ast analysis
    os.remove(filename)
    # then, check to see if ast visitor found any constraint violations
    num_fdefs = len(ast_analysis["fdefs"].keys())
    constraints_vlen = len(ast_analysis["constraint_violation"])
    # if num_fdefs != 1:
    #     return Response("POST NOT OK: Too few or too many function(s) => {0}".format(num_fdefs), status=status.HTTP_400_BAD_REQUEST)
    if constraints_vlen > 0:
        print("POST NOT OK: constraint violation(s) : {0}" .format(ast_analysis["constraint_violation"]))
        return Response(12, status=status.HTTP_400_BAD_REQUEST) # 12 is error code for constraint violation
    return True
