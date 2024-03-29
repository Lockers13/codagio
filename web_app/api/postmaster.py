### module to perform general post operations

from code_analysis.models import Problem, Solution
from users.models import Profile
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from app import settings
from datetime import datetime
import json 
from code_analysis import forms as ca_forms
from ca_modules import make_utils

ERROR_CODES = settings.SUBMISSION_ERROR_CODES

def retrieve_form_data(form, submission_type="solution"):
    """Quick utility function that groups together the processing of request data. Allows for easier handling of exceptions
    Takes request object as argument
    On Success, returns hashmap of processed data...otherwise raise an exception"""

    if submission_type == "solution":
        processed_data = {}
        try:
            print("FCD =>", form.cleaned_data)
            processed_data["prob_id"] = int(form.cleaned_data.get("problem_id"))
            processed_data["uid"] = int(form.cleaned_data.get("user_id"))
            processed_data["code_data"] = form.cleaned_data.get("solution")
            processed_data["course_id"] = form.cleaned_data.get("course_id", None)
        except Exception as e:
            print("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        return processed_data

    elif submission_type == "problem_upload":
        data = form.cleaned_data
        processed_data = {}
        try:
            processed_data["author_id"] = int(data.get("author_id"))
            processed_data["category"] = data.get("category")
            processed_data["target_file"] = data.get("target_file", None)
            processed_data["data_file"] = data.get("data_file", None)
            processed_data["course_id"] = data.get("course_id", None)
            if processed_data["data_file"] is not None:
                processed_data["data_file"].seek(0)
                processed_data["init_data"] = processed_data["data_file"].read().decode("utf-8")
                try:
                    json.loads(processed_data["init_data"])
                except Exception as e:
                    raise Exception("Invalid JSON in init_data_file! - {0}".format(str(e)))
            else:
                processed_data["init_data"] = None
            processed_data["name"] = data.get("name").replace("(", "[").replace(")", "]")
            if "(" in processed_data["name"] or ")" in processed_data["name"]:
                print("POST NOT OK: Problem Name cannot contain parnetheses!")
                return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
            description = data.get("description")
            processed_data["program_file"] = data.get("program")
            processed_data["code"] = [line.decode("utf-8") for line in processed_data["program_file"].read().splitlines()]
            processed_data["metadata"] = data.get("meta_file")
            processed_data["metadata"]["description"] = description
            processed_data["date_submitted"] = datetime.now()
            processed_data["inputs"] = data.get("inputs", None)
            if processed_data["category"] == "file_io":
                 processed_data["metadata"]["inputs"] = "file"
            else:
                processed_data["metadata"]["inputs"] = True if processed_data["inputs"] is not None else False
            processed_data["metadata"]["init_data"] = True if processed_data["init_data"] is not None else False
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
        except Exception as e:
            print("POST NOT OK: uid db error (error getting author) => {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return author

def get_uploaded_form(request, problem=True):
    if problem:
        category_forms = {
            'file_io': ca_forms.IOProblemUploadForm(request.POST, request.FILES),
            'default': ca_forms.DefaultProblemUploadForm(request.POST, request.FILES),
        }
        return category_forms[request.data["category"]]
    else:
        return ca_forms.SolutionSubmissionForm(request.POST)

def get_sample_inputs_outputs(filename, processed_data):
    def file_io():
        input_hash = make_utils.handle_uploaded_file_inputs(processed_data)
        files = ["{0}.py".format(x) for x in input_hash["files"].keys()]
        processed_data["inputs"] = files
        outputs = make_utils.gen_sample_outputs(filename, processed_data, init_data=processed_data["init_data"], input_type="file")
        processed_data["inputs"] = input_hash
        return input_hash, outputs
    def default():
        inputs = processed_data["inputs"]
        outputs = make_utils.gen_sample_outputs(filename, processed_data, init_data=processed_data["init_data"])
        return inputs, outputs

    switch_dict = {
        'file_io': file_io,
        'default': default,
    }

    return switch_dict[processed_data["category"]]()
