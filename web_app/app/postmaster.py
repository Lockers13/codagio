### module to perform general post operations

from code_analysis.models import Problem, Solution
from users.models import Profile
from rest_framework import generics, status
from rest_framework.response import Response
from . import settings

ERROR_CODES = settings.SUBMISSION_ERROR_CODES

def retrieve_form_data(request, submission_type="solution"):
    """Quick utility function that groups together the processing of request data. Allows for easier handling of exceptions
    Takes request object as argument
    On Success, returns hashmap of processed data...otherwise raise an exception"""

    if submission_type == "solution":
        processed_data = {}
        try:
            processed_data["prob_id"] = int(request.data.get("problem_id"))
            processed_data["uid"] = request.user.id
            processed_data["code_data"] = request.data.get("solution")
        except Exception as e:
            print("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        return processed_data

def load_problem_data(problem):
    problem_data = {}
    try:
        problem_data["init_data"] = problem.init_data
        problem_data["metadata"] = problem.metadata
        problem_data["inputs"] = problem.inputs
        problem_data["outputs"] = problem.outputs
        problem_data["analysis"] = problem.analysis        
    except Exception as e:
        print("POST NOT OK: Error during loading of problem data - {0}".format(str(e)))
        return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return problem_data

def write_initial_file(problem_name, code_data):
    filename = "{0}.py".format('_'.join(problem_name.split()))
    with open(filename, 'w') as f:
        f.write(code_data)
    return filename

def write_executable_file():
    pass

def get_relevant_db_entries(data, submission_type="solution"):
    if submission_type == "solution":
        try:
            problem = Problem.objects.filter(id=data["prob_id"]).first()
        except Exception as e:
            print("POST NOT OK: reference problem db exception = {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            user = Profile.objects.filter(id=data["uid"]).first()
        except Exception as e:
            print("POST NOT OK: uid db exception = {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return problem, user
    