import os
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_utils, comparison
from ca_modules.analyzer import Analyzer
from datetime import datetime
from .models import Problem, Solution
from users.models import Profile
from django.shortcuts import render, redirect
from . import forms as submission_forms
from django.contrib.auth.models import User
import yaml
from app import postmaster as pm
from app import settings
from . import forms as ca_forms

ERROR_CODES = settings.SUBMISSION_ERROR_CODES

### NB: When hashmaps (dicts) are saved as jsonb to postgres, their keys are ordered by length, and then alphabetically
### This is a change from the order in which they are created on our python backend, and if we need to make our pythonic dicts
### conform to the ordering of the ones retrieved from our db, then we can use 'make_utils.json_reorder(hashmap)'

class AnalysisView(APIView):
    """Class based view for handling the analysis of submitted solutions"""

    ### only 'post' requests to this API endpoint are allowed
    http_method_names = ['post']

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""

        processed_data = pm.retrieve_form_data(request, submission_type="solution")
        uploaded_form = ca_forms.SolutionSubmissionForm(request.POST, request.FILES)
        try:
            uploaded_form.is_valid()
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        ### get problem instance from DB
        ret_obj = pm.get_relevant_db_entries(processed_data, submission_type="solution")
        
        if isinstance(ret_obj, Response):
            return ret_obj
        else:
            problem, user = ret_obj

        problem_data = pm.load_problem_data(problem)
        if isinstance(problem_data, Response):
            return problem_data

        ### make basic initial file from code_data for the sole purposes of ast parsing
        filename = pm.write_initial_file(problem.name, processed_data["code_data"], submission_type="solution")

        ### analyze submitted solution (at ast level) against reference problem metadata - passing metadata allows us to access constraint variables
        analyzer = Analyzer(filename, problem_data["metadata"])
        
        try:
            validation_result = analyzer.visit_ast()
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            os.remove(filename)
            return Response(ERROR_CODES["Syntax Error"], status=status.HTTP_400_BAD_REQUEST)
        
        if validation_result == False:
            os.remove(filename)
            return Response(ERROR_CODES["Constraint Violation"], status=status.HTTP_400_BAD_REQUEST)

        ### after discarding first file used during ast analysis, now create full-fledged script capable of processing inputs passed from command line (cf. verification stage)
        ### but first check what kind of problem input we are dealing with (viz. 'auto generated', 'file io', etc.)

        code_data = processed_data["code_data"].splitlines()

        try:
            make_utils.make_file(filename, code_data, problem_data)
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        ### verify the submitted solution against the appropriate reference problem
        try:
            percentage_score = analyzer.verify(problem_data)
        except Exception as e:
            msg = str(e)
            print("POST NOT OK: {0}".format(msg))
            if "semantic" in msg:
                return Response(ERROR_CODES["Semantic Error"], status=status.HTTP_400_BAD_REQUEST)
            elif "retcode = 124" in msg:
                return Response(ERROR_CODES["Timeout Error"], status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ### check if all tests were passed, and only profile submission if so (both lprof and cprof)
        hundred_pc = float(percentage_score) == 100.0

        if hundred_pc:
            try:
                # default kwarg is init_data=None
                analyzer.profile(problem_data["inputs"], init_data=problem_data["init_data"])            
            except Exception as e:
                print("POST NOT OK: {0}".format(str(e)))
                return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
        ### get analysis dict

        analysis = analyzer.get_prog_dict()
        analysis["ref_time"] = problem.analysis["udef_func_time_tot"]
        ### write comparison stats (with reference problem) to analysis dict
        comparison.write_comp(analysis, problem_data["analysis"])         
        ### only save submitted solution to db if all tests were passed, and hence submission was profiled, etc.
        if hundred_pc:
            solution, created = Solution.objects.update_or_create(
                submitter_id=processed_data["uid"],
                problem_id=processed_data["prob_id"],
                defaults={'analysis': analysis, 'date_submitted': datetime.now()}
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

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""
        ### get data, process it, and handle errors
        processed_data = pm.retrieve_form_data(request, submission_type="problem_upload")
        print(processed_data)
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        
        if processed_data["category"] == "file_io":
            uploaded_form = ca_forms.IOProblemUploadForm(request.POST, request.FILES)
        elif processed_data["category"] == "default":
            uploaded_form = ca_forms.DefaultProblemUploadForm(request.POST, request.FILES)
        
        try:
            uploaded_form.is_valid()
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)

        if processed_data["metadata"]["main_function"] in ["main", "prep_input"]:
            return Response(ERROR_CODES["Constraint Violation"], status=status.HTTP_400_BAD_REQUEST)
        ### get author instance from DB
        author = pm.get_relevant_db_entries(processed_data, submission_type="problem_upload")
        if isinstance(author, Response):
            return author
            
        filename = pm.write_initial_file(processed_data["name"], processed_data["program_file"], submission_type="problem_upload")

        ### create analyzer instance, passing script to be visited by ast_visitor, as well as uploaded metadata...subsequent checks may be overkill - needs review (are you really going to violate your own constraints? maybe by accident...)
        analyzer = Analyzer(filename, processed_data["metadata"])

        ### visit ast, do static analysis, and check for constraint violations
        try:
            validation_result = analyzer.visit_ast()
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            os.remove(filename)
            return Response(ERROR_CODES["Syntax Error"], status=status.HTTP_400_BAD_REQUEST)
        
        if validation_result == False:
            os.remove(filename)
            return Response(ERROR_CODES["Constraint Violation"], status=status.HTTP_400_BAD_REQUEST)

        code_data = processed_data["code"]

        if processed_data["data_file"] is not None:
            processed_data["data_file"].seek(0)
            processed_data["init_data"] = processed_data["data_file"].read().decode("utf-8")
        else:
            processed_data["init_data"] = None

        make_utils.make_file(filename, code_data, processed_data)

        ### Depending on the type of uploaded problem, the processes for making an executable script, generating inputs, and generating outputs, will be different
        ### These different eventualities are handled below
        if processed_data["category"] == "file_io":
            problem_inputs, files = make_utils.handle_uploaded_file_inputs(processed_data)
            input_hash = problem_inputs
            outputs = make_utils.gen_sample_outputs(filename, files, init_data=processed_data["init_data"], input_type="file")

        elif processed_data["category"] == "default":
            input_hash = {"default": {}}
            try:
                processed_data["inputs"].seek(0)
                problem_inputs = json.loads(processed_data["inputs"].read().decode("utf-8"))  
            except Exception as e:
                print("Invalid upload: {0}".format(str(e)))
                return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
            input_hash["default"]["custom"] = problem_inputs
            ### generate sample outputs, given auto-generated or custom inputs
            outputs = make_utils.gen_sample_outputs(filename, problem_inputs, init_data=processed_data["init_data"])
 
        ### profile uploaded reference problem (will only do cProfile and not line_profile as 'solution' is set to false)
        analyzer.profile(input_hash, solution=False, init_data=processed_data["init_data"])
        ### get final analysis dict
        analysis = analyzer.get_prog_dict()
        
        ### save uploaded problem, with associated inputs, outputs, and metadata to DB
        problem, created = Problem.objects.update_or_create(
            name=processed_data["name"], author_id=processed_data["author_id"],
            defaults = {
                'outputs': outputs,
                'metadata': processed_data["metadata"],
                'inputs': input_hash,
                'analysis': analysis,
                'init_data': processed_data["init_data"],
                'date_submitted': processed_data["date_submitted"],
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
    metadata = problem.metadata
    difficulty = metadata['difficulty']
    description = metadata['description']
    main_signature = problem.analysis.get("main_signature", None)

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
                'main_signature': main_signature,
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

def problem_view(request, category):
    problems = Problem.objects.filter(metadata__category__contains=category).all()
    ### turn inner json dict into python dict before passing to template
    context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems, 'category': category}
    return render(request, 'problem_view.html', context)