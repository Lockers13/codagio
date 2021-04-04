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


ERROR_CODES = {
    "Semantic Error": 10,
    "Syntax Error": 11,
    "Constraint Violation": 12,
    "Server-Side Error": 13,
    "Timeout Error": 14
}

### NB: When hashmaps (dicts) are saved as jsonb to postgres, their keys are ordered by length, and then alphabetically
### This is a change from the order in which they are created on our python backend, and if we need to make our pythonic dicts
### conform to the ordering of the ones retrieved from our db, then we can use 'make_utils.json_reorder(hashmap)'

class AnalysisView(APIView):
    """Class based view for handling the analysis of submitted solutions"""

    ### only 'post' requests to this API endpoint are allowed
    http_method_names = ['post']

    def __load_problem_data(self, problem):
        problem_data = {}
        try:
            problem_data["init_data"] = problem.init_data
            problem_data["metadata"] = problem.metadata
            problem_data["inputs"] = problem.inputs
            problem_data["outputs"] = problem.outputs
            problem_data["analysis"] = problem.analysis        
        except Exception as e:
            print("POST NOT OK: Error during loading of problem json - {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return problem_data

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
            print("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
            print("POST NOT OK: reference problem db exception = {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        problem_data = self.__load_problem_data(problem)

        if isinstance(problem_data, Response):
            return problem_data

        prob_name = problem.name
        ### get user instance from DB
        try:
            user = Profile.objects.filter(id=processed_data["uid"]).first()
        except Exception as e:
            print("POST NOT OK: uid db exception = {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        filename = "{0}.py".format(prob_name)
        ### checking with mock validation (seems obsolete as placeholder, maybe remove)
        if not validate_submission(processed_data["code_data"]):
            print("POST NOT OK: invalid code!")
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'w') as f:
            f.write(processed_data["code_data"])

        ### analyze submitted solution (at ast level) against reference problem metadata - passing metadata allows us to access constraint variables
        analyzer = Analyzer(filename, problem_data["metadata"])
        try:
            analyzer.visit_ast()
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            os.remove(filename)
            return Response(ERROR_CODES["Syntax Error"], status=status.HTTP_400_BAD_REQUEST)
        
        ### if the ast_visitor has picked up on any constraint violations then return appropriate error status
        ast_analysis = analyzer.get_prog_dict()
        ### validate results of ast analysis by checking length of certain lists that hold violation data, if any
        validation_result = ast_checker.validate(ast_analysis, filename)
        if isinstance(validation_result, Response):
            return validation_result
        
        ### after discarding first file used during ast analysis, now create full-fledged script capable of processing inputs passed from command line (cf. verification stage)
        ### but first check what kind of problem input we are dealing with (viz. 'auto generated', 'file io', etc.)
        input_type = next(iter(problem_data["metadata"].get("input_type")))
        if input_type == "file":
            if problem_data["init_data"] is not None:
                make_utils.make_file(filename, processed_data["code_data"].splitlines(), input_type="file", init_data=True, main_function=problem_data["metadata"]["main_function"])
            else:
                make_utils.make_file(filename, processed_data["code_data"].splitlines(), input_type="file", main_function=problem_data["metadata"]["main_function"])
        elif input_type == "auto" or input_type == "custom":
            try:
                make_utils.make_file(filename, processed_data["code_data"].splitlines(), main_function=problem_data["metadata"]["main_function"])
            except Exception as e:
                print("POST NOT OK: {0}".format(str(e)))
                return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        ### verify the submitted solution against the appropriate reference problem

        try:
            percentage_score = analyzer.verify(problem_data)
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            if "semantic" in str(e):
                return Response(ERROR_CODES["Semantic Error"], status=status.HTTP_400_BAD_REQUEST)
            elif "retcode = 124" in str(e):
                return Response(ERROR_CODES["Timeout Error"], status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ### check if all tests were passed, and only profile submission if so (both lprof and cprof)
        hundred_pc = float(percentage_score) == 100.0
        if hundred_pc:
            try:
                if problem_data["init_data"] is not None:
                    analyzer.profile(problem_data["inputs"], init_data=problem_data["init_data"])
                else:
                    analyzer.profile(problem_data["inputs"])                   
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

    def __validate_custom_inputs(self, custom_input):
        # try:
        #     custom_input
        #     if len(custom_input) > 3:
        #         return Response("POST NOT OK: Too many tests!", status=status.HTTP_400_BAD_REQUEST)
        #     else:
        #         for inp in custom_input:
        #             if not isinstance(inp, list):
        #                 return Response("POST NOT OK: Incorrectly formatted custom inputs!", status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response("POST 1NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return True

    def __process_request_data(self, data):
        """Utility function to process received request data. Takes data object (dict) as argument

        Returns processed data dict on success, otherwise error response"""

        processed_data = {}
        try:
            processed_data["author_id"] = int(data.get("author_id"))
            processed_data["category"] = data.get("category")
            processed_data["target_file"] = data.getlist("target_file", None)
            processed_data["data_file"] = data.get("data_file", None)
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
            return Response("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return processed_data

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""

        ### get data, process it, and handle errors
        data = request.data
        processed_data = self.__process_request_data(data)
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        if processed_data["metadata"]["main_function"] in ["main", "prep_input"]:
            return Response("POST NOT OK: main_function cannot be called 'main' or 'prep_input'", status=status.HTTP_400_BAD_REQUEST)

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
        ### chunkwise writing is unnecessay since we impose file size restrictions of the client side, but we leave it in anyway (as probably more efficient to deal with bytes rather than decoded strings)
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
            return Response("POST NOfdbT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### if the ast_visitor has picked up on any constraint violations then return appropriate error response
        ast_analysis = analyzer.get_prog_dict()
        validation_result = ast_checker.validate(ast_analysis, filename)
        
        if isinstance(validation_result, Response):
            return validation_result

        ### Depending on the type of uploaded problem, the processes for making an executable script, generating inputs, and generating outputs, will be different
        ### These different eventualities are handled below
        if processed_data["category"] == "file_io":
            if processed_data["data_file"] is not None and processed_data["data_file"] != "":
                make_utils.make_file(filename, processed_data["code"], input_type="file", init_data=True, main_function=processed_data["metadata"]["main_function"])
                problem_inputs, files = make_utils.handle_uploaded_file_inputs(processed_data)
                ### generate sample outputs, given file inputs
                init_data = processed_data["data_file"].read().decode("utf-8")
                outputs = make_utils.gen_sample_outputs(filename, files, init_data=init_data, input_type="file")
                input_hash = problem_inputs
            else:
                ### make new script capable of being verified and profiled
                make_utils.make_file(filename, processed_data["code"], input_type="file", main_function=processed_data["metadata"]["main_function"])
                ### generate file inputs, given processed data
                problem_inputs, files = make_utils.handle_uploaded_file_inputs(processed_data)
                ### generate sample outputs, given file inputs
                outputs = make_utils.gen_sample_outputs(filename, files, input_type="file")
                input_hash = problem_inputs
                init_data = None

        elif processed_data["category"] == "default":
            input_hash = {}
            input_hash["default"] = {}
            ### make new script capable of being verified and profiled
            make_utils.make_file(filename, processed_data["code"], main_function=processed_data["metadata"]["main_function"])
            ### check whether custom inputs are provided (in json format), 
            ### or whether they are to be auto generated as per specifications of metadata file

            problem_inputs = json.loads(processed_data["inputs"].read().decode("utf-8"))
            validated_input = self.__validate_custom_inputs(problem_inputs)
            if isinstance(validated_input, Response):
                return validated_input
            input_hash["default"]["custom"] = problem_inputs

            # else:
            #     ### just shortening overly verbose data references
            #     input_type = processed_data["metadata"].get("input_type")["auto"]
            #     input_length = processed_data["metadata"].get("input_length", None)
            #     num_tests = processed_data["metadata"].get("num_tests", None)
            #     ### auto-generate inputs, given relevant metadata
            #     problem_inputs = make_utils.generate_input(input_type, input_length, num_tests)
            #     input_hash["default"]["auto"] = problem_inputs

            ### generate sample outputs, given auto-generated or custom inputs
            init_data = None  
            outputs = make_utils.gen_sample_outputs(filename, problem_inputs)
 

        ### profile uploaded reference problem (will only do cProfile and not line_profile as 'solution' is set to false)
        analyzer.profile(input_hash, solution=False, init_data=init_data)
        ### get final analysis dict
        analysis = analyzer.get_prog_dict()

        try:
            init_data
        except Exception as e:
            init_data = None
        
        ### save uploaded problem, with associated inputs, outputs, and metadata to DB
        problem, created = Problem.objects.update_or_create(
            name=processed_data["name"], author_id=processed_data["author_id"],
            defaults = {
                'outputs': outputs,
                'metadata': processed_data["metadata"],
                'inputs': input_hash,
                'analysis': analysis,
                'init_data': init_data,
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
