import os
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_utils, comparison, ast_checker
from ca_modules.analyzer import Analyzer
from datetime import datetime
from .models import Problem, Solution
from users.models import Profile
from django.shortcuts import render, redirect
from . import forms as submission_forms
from django.contrib.auth.models import User
import yaml

class AnalysisView(APIView):
    """Class based view for handling the analysis of submitted solutions"""

    ### only 'post' requests to this API endpoint are allowed
    http_method_names = ['post']

    def __process_request_data(self, request):
        """Quick utility function that groups together the processing of request data. Allows for easier handling of exceptions
        Takes request object as argument
        On Success, returns hashmap of processed data...otherwise raise an exception"""

        processed_data = {}
        try:
            processed_data["prob_id"] = int(request.data.get("problem_id"))
            processed_data["uid"] = request.user.id
            processed_data["code_data"] = request.data.get("solution")
        except Exception as e:
            return Response("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return processed_data

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""

        def validate_submission(sub):
            ### mock validation function
            if not sub:
                raise ValidationError(
                    _('%(sub)s is not valid code'),
                    params={'sub': sub},
                )
            return True


        processed_data = self.__process_request_data(request)
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        ### get problem instance from DB
        try:
            problem = Problem.objects.filter(id=processed_data["prob_id"]).first()
        except Exception as e:
            return Response("POST NOT OK: reference problem db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        prob_name = problem.name
        ### get user instance from DB
        try:
            user = Profile.objects.filter(id=processed_data["uid"]).first()
        except Exception as e:
            return Response("POST NOT OK: uid db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        filename = "{0}.py".format(prob_name)
        ### checking with mock validation (seems obsolete as placeholder, maybe remove)
        if not validate_submission(processed_data["code_data"]):
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'w') as f:
            f.write(processed_data["code_data"])
        ### analyze submitted solution (at ast level) against reference problem metadata - passing metadata allows us to access constraint variables
        metadata = json.loads(problem.metadata)
        analyzer = Analyzer(filename, metadata)
        try:
            analyzer.visit_ast()
        except Exception as e:
            os.remove(filename)
            return Response("POST NOG\QT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        
        ### if the ast_visitor has picked up on any constraint violations then return appropriate error status
        ast_analysis = analyzer.get_prog_dict()
        ### validate results of ast analysis by checking length of certain lists that hold violation data, if any
        validation_result = ast_checker.validate(ast_analysis, filename)
        if isinstance(validation_result, Response):
            return validation_result
        
        ### after discarding first file used during ast analysis, now create full-fledged script capable of processing inputs passed from command line (cf. verification stage)
        ### but first check what kind of problem input we are dealing with (viz. 'auto generated', 'file io', etc.)
        input_type = next(iter(metadata.get("input_type")))
        if input_type == "file":
            make_utils.make_file(filename, processed_data["code_data"], input_type="file")
        elif input_type == "auto":
            make_utils.make_file(filename, processed_data["code_data"])
        ### verify the submitted solution against the appropriate reference problem
        try:
            percentage_score = analyzer.verify(problem)
        except Exception as e:
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### check if all tests were passed, and only profile submission if so (both lprof and cprof)
        hundred_pc = float(percentage_score) == 100.0
        if hundred_pc:
            try:
                analyzer.profile(problem.inputs)
            except Exception as e:
                return Response("POST NOAAT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### get analysis dict
        analysis = analyzer.get_prog_dict()
        ### write comparison stats (with reference problem) to analysis dict
        comparison.write_comp(analysis, json.loads(problem.analysis))         
        ### only save submitted solution to db if all tests were passed, and hence submission was profiled, etc.
        if hundred_pc:
            solution, created = Solution.objects.update_or_create(
                submitter_id=processed_data["uid"],
                problem_id=processed_data["prob_id"],
                defaults={'analysis': json.dumps(analysis), 'date_submitted': datetime.now()}
            )
            solution.save()
        ### discard preprocessed executable script
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        ### return analysis within successful http response
        return Response(json.dumps(analysis), status=status.HTTP_200_OK)

class SaveProblemView(APIView):
    """Class based API view for handling the uploading of a reference problem"""

    ### only allow 'post' requests to this api endpoint
    http_method_names = ['post']

    def __process_request_data(self, data):
        """Utility function to process received request data. Takes data object (dict) as argument

        Returns processed data dict on success, otherwise error response"""

        processed_data = {}
        try:
            processed_data["author_id"] = int(data.get("author_id"))
            processed_data["category"] = data.get("category")
            processed_data["input_files"] = data.getlist("input_files", None)
            processed_data["custom_inputs"] = data.get("custom_inputs", None)
            processed_data["name"] = data.get("name")
            description = data.get("description")
            processed_data["program_file"] = data.get("program")
            processed_data["code"] = [line.decode("utf-8") for line in processed_data["program_file"].read().splitlines()]
            meta_file = data.get("meta_file")
            processed_data["metadata"] = yaml.full_load(meta_file.read())
            processed_data["metadata"]["description"] = description
            processed_data["metadata"]["date_created"] = datetime.now()
        except Exception as e:
            return Response("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return processed_data

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""

        ### get data, process it, and handle errors
        data = request.data
        print("HEYO DATA =>", data)
        processed_data = self.__process_request_data(data)
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        ### get author instance from DB
        try:
            author = User.objects.filter(id=processed_data.get("author_id")).first()
            ### only allow registered superusers to upload problems - this feature may need reviewing!
            if not author.is_superuser:
                return Response("POST NOT OK: problem author is not superuser!", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("POST NOT OK: author db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        filename = "{0}.py".format(processed_data["name"])

        ### make basic initial file from uploaded in-memory file obj for the purposes of ast parsing
        ### chunk-wise write in order to prevent against massive file uploads overloading server
        with open(filename, 'wb+') as f:
            for chunk in processed_data["program_file"].chunks():
                f.write(chunk)

        ### create analyzer instance, passing script to be visited by ast_visitor, as well as uploaded metadata...subsequent checks may be overkill - needs review (are you really going to violate your own constraints? maybe by accident...)
        analyzer = Analyzer(filename, processed_data["metadata"])

        ### visit ast, do static analysis, and check for constraint violations
        try:
            analyzer.visit_ast()
        except Exception as e:
            os.remove(filename)
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### if the ast_visitor has picked up on any constraint violations then return appropriate error response
        ast_analysis = analyzer.get_prog_dict()
        validation_result = ast_checker.validate(ast_analysis, filename)
        if isinstance(validation_result, Response):
            return validation_result
        
        ### Depending on the type of uploaded problem, the processes for making an executable script, generating inputs, and generating outputs, will be different
        ### These different eventualities are handled below
        if processed_data["category"] == "file_io":
            ### make new script capable of being verified and profiled
            make_utils.make_file(filename, processed_data["code"], source="file", input_type="file")
            ### generate file inputs, given processed data
            problem_inputs, files = make_utils.handle_uploaded_file_inputs(processed_data)
            ### generate sample outputs, given file inputs
            outputs = make_utils.gen_sample_outputs(filename, files, input_type="file")

        elif processed_data["category"] == "default":
            ### make new script capable of being verified and profiled
            make_utils.make_file(filename, processed_data["code"], source="file")
            ### check whether custom inputs are provided (in json format), 
            ### or whether they are to be auto generated as per specifications of metadata file
            if processed_data["custom_inputs"] is not None:
                problem_inputs = processed_data["custom_inputs"].read().decode("utf-8")
            else:
                ### just shortening overly verbose data references
                input_type = processed_data["metadata"].get("input_type")["auto"]
                input_length = processed_data["metadata"].get("input_length", None)
                num_tests = processed_data["metadata"].get("num_tests", None)
                ### auto-generate inputs, given relevant metadata
                problem_inputs = make_utils.generate_input(input_type, input_length, num_tests)
            ### generate sample outputs, given auto-generated inputs
            outputs = make_utils.gen_sample_outputs(filename, problem_inputs)

        ### profile uploaded reference problem (will only do cProfile and not line_profile as 'solution' is set to false)
        analyzer.profile(problem_inputs, solution=False)
        ### get final analysis dict
        analysis = json.dumps(analyzer.get_prog_dict())
        ### save uploaded problem, with associated inputs, outputs, and metadata to DB
        problem, created = Problem.objects.update_or_create(
            name=processed_data["name"], author_id=processed_data["author_id"],
            defaults = {
                'outputs': json.dumps(outputs),
                'metadata': json.dumps(processed_data["metadata"], default=str),
                'inputs': problem_inputs,
                'analysis': analysis
                }
            )
        problem.save()
        ### finally remove previously generated executable script from disk and return success response
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        return Response("POST OK", status=status.HTTP_200_OK)


### below are two function based views for determining which forms are presented to users when they choose
### either to upload a solution, or upload a problem

def solution_upload(request, prob_id):
    ### get problem (and all associated metadata) from DB, and set initial state accordingly
    problem = Problem.objects.get(id = prob_id)
    metadata = json.loads(problem.metadata)
    difficulty = metadata['difficulty']
    description = metadata['description']

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    ### load appropriate form
    form = submission_forms.SolutionSubmissionForm(initial=initial_state)

    ### set template context
    context = { 'title': 'CGC | Home',
                'form': form,
                'difficulty':difficulty,
                'problem_name':problem.name,
                'problem_desc':description,
                }

    return render(request, 'code.html', context)

def problem_upload(request, problem_cat):
    ### obviously, since the user is creating a problem, there is no problem data to retrieve from DB
    ### nevertheless we minimally set the initial state of the form with the small amount of data we do have
    initial_state = {
        'author_id': request.user.id,
        'category': problem_cat,
    }
    ### check the type of problem being uploaded, and load appropriate form
    if problem_cat == "default":
        form = submission_forms.DefaultProblemUploadForm(initial=initial_state)
    elif problem_cat == "file_io":
        form = submission_forms.IOProblemUploadForm(initial=initial_state)

    ### set template context
    context = { 'title': 'CGC | Home',
                'form': form,
                'cat': problem_cat,
                }

    return render(request, 'problem_upload.html', context)