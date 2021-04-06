### module to perform general post operations

from code_analysis.models import Problem, Solution
from users.models import Profile
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from . import settings
from datetime import datetime
import yaml
import json 

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

    elif submission_type == "problem_upload":
        data = request.data
        processed_data = {}
        try:
            processed_data["author_id"] = int(data.get("author_id"))
            processed_data["category"] = data.get("category")
            processed_data["target_file"] = data.get("target_file", None)
            processed_data["data_file"] = data.get("data_file", None)
            ### unsure why django optional file left empty is uploaded as empty string and not 'null'
            if processed_data["data_file"] == "":
                processed_data["data_file"] = None
            processed_data["name"] = data.get("name")
            description = data.get("description")
            processed_data["program_file"] = data.get("program")
            processed_data["code"] = [line.decode("utf-8") for line in processed_data["program_file"].read().splitlines()]
            meta_file = data.get("meta_file")
            processed_data["metadata"] = yaml.safe_load(meta_file.read())
            processed_data["metadata"]["description"] = description
            processed_data["date_submitted"] = datetime.now()
            processed_data["inputs"] = data.get("inputs", None)
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

def write_initial_file(problem_name, code_data, submission_type="solution"):
    filename = "{0}.py".format('_'.join(problem_name.lower().split()))
    if submission_type == "solution":
        with open(filename, 'w') as f:
            f.write(code_data)
    elif submission_type == "problem_upload":
        with open(filename, 'wb+') as f:
            for chunk in code_data.chunks():
                f.write(chunk)
    return filename

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
    elif submission_type == "problem_upload":
        try:
            author = User.objects.filter(id=data.get("author_id")).first()
            ### only allow registered superusers to upload problems - this feature may need reviewing!
            if not author.is_superuser:
                print("POST NOT OK: author not superuser")
                return Response(ERROR_CODES["Permission Denied Error"], status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print("POST NOT OK: uid db error (error getting author) => {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return author




    