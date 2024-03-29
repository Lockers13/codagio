import os
import json
import yaml
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from code_analysis.models import Problem, Solution
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_utils, comparison
from ca_modules.analyzer import Analyzer
from datetime import datetime
from users.models import Profile
from django.contrib.auth.models import User
from . import postmaster as pm
from app import settings
from code_analysis import forms as ca_forms
from classes.models import Course, Enrolment
import hashlib
from django.utils import timezone


################################################ code analysis API endpoints #######################################

ERROR_CODES = settings.SUBMISSION_ERROR_CODES

class AnalysisView(APIView):
    """Class based view for handling the analysis of submitted solutions"""

    ### only 'post' requests to this API endpoint are allowed
    http_method_names = ['post']

    def post(self, request):
        """Built-in django function to handle post requests to API endpoint
        
        Returns an HTTP response of some kind"""

        def prune_analysis():
            for _, v in analysis["scores"].items():
                try:
                    if v["detailed_stats"]["submitter_visible"] == False:
                        v["detailed_stats"]["input"] = None
                        v["detailed_stats"]["reference_output"] = None
                        v["detailed_stats"]["user_output"] = None
                except Exception as e:
                    pass

        
        
        uploaded_form = pm.get_uploaded_form(request, problem=False)

        try:
            if not uploaded_form.is_valid():
                return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        
        processed_data = pm.retrieve_form_data(uploaded_form, submission_type="solution")
        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data
        ### get problem instance from DB
        
        ret_obj = pm.get_relevant_db_entries(processed_data, submission_type="solution")
        
        if isinstance(ret_obj, Response):
            return ret_obj
        else:
            problem, user = ret_obj

        # check whether number of allowed attempts has been exceeded - default (i.e. if not specified in metafile) is 10
        attempts_allowed = problem.metadata.get("attempts_allowed", 10)
        num_solutions = len(list(Solution.objects.filter(problem_id=problem.id).filter(submitter_id=request.user.id).all()))
        if num_solutions >= attempts_allowed:
            return Response(ERROR_CODES["Attempt Limit Exceeded"], status=status.HTTP_400_BAD_REQUEST)

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
            print("POSTdd NOT OK: {0}".format(msg))
            if "semantic" in msg:
                return Response(ERROR_CODES["Semantic Error"], status=status.HTTP_400_BAD_REQUEST)
            elif "retcode = 124" in msg:
                return Response(ERROR_CODES["Timeout Error"], status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ### check if all tests were passed, and only profile submission if so (both lprof and cprof)
        passed = float(percentage_score) >= float(problem_data["metadata"]["pass_threshold"])

        try:
            # default kwarg is init_data=None
            analyzer.profile(problem_data)            
        except Exception as e:
            print("POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Server-Side Error"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        ### get analysis dict

        analysis = analyzer.get_prog_dict()
        
        analysis["ref_time"] = problem.analysis["udef_func_time_tot"]
        analysis["ref_phys_mem"] = problem.analysis["total_physical_mem"]
        analysis["ref_virt_mem"] = problem.analysis["total_virtual_mem"]
        if not problem.metadata.get("time_profile"):
            analysis["time_profile"] = False
        else:
            analysis["time_profile"] = True
        analysis["pass_threshold"] = problem_data["metadata"]["pass_threshold"]
        analysis["solution_text"] = code_data
        analysis["score"] = percentage_score
        analysis["passed"] = passed
        ### write comparison stats (with reference problem) to analysis dict
        comparison.write_comp(analysis, problem_data["analysis"])
        print("Course_ID =>", processed_data["course_id"])       
        ### only save submitted solution to db if all tests were passed, and hence submission was profiled, etc.
        ### !!! TODO: Need to limit uploads à la leetcode (resource exhaustion), and number of tries !!!
        Solution.objects.create(
            submitter_id=processed_data["uid"],
            problem_id=processed_data["prob_id"],
            course_id=processed_data["course_id"],
            analysis=analysis, 
            date_submitted=timezone.now()
        )
        ### discard preprocessed executable script
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        
        # we only want to show users the inputs/outputs for the first incorrect solution
        prune_analysis()
        analysis["num_solutions"] = num_solutions + 1
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
        # processed_data = pm.retrieve_form_data(request, submission_type="problem_upload")

        uploaded_form = pm.get_uploaded_form(request)

        try:
            if not uploaded_form.is_valid():
                return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("1POST NOT OK: {0}".format(str(e)))
            return Response(ERROR_CODES["Form Submission Error"], status=status.HTTP_400_BAD_REQUEST)

        processed_data = pm.retrieve_form_data(uploaded_form, submission_type="problem_upload")

        ### if an error response was returned from processing function, then return it from this view
        if isinstance(processed_data, Response):
            return processed_data

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
            print("2POST NOT OK: {0}".format(str(e)))
            os.remove(filename)
            return Response(ERROR_CODES["Syntax Error"], status=status.HTTP_400_BAD_REQUEST)
        
        if validation_result == False:
            os.remove(filename)
            return Response(ERROR_CODES["Constraint Violation"], status=status.HTTP_400_BAD_REQUEST)

        code_data = processed_data["code"]

        make_utils.make_file(filename, code_data, processed_data)

        inputs, outputs = pm.get_sample_inputs_outputs(filename, processed_data)
        ### profile uploaded reference problem (will only do cProfile and not line_profile as 'solution' is set to false)
        analyzer.profile(processed_data, solution=False)
        ### get final analysis dict
        analysis = analyzer.get_prog_dict()
        analysis["code_data"] = code_data
        print("HI")

        ### save uploaded problem, with associated inputs, outputs, and metadata to DB
        problem, created = Problem.objects.update_or_create(
            name=processed_data["name"], author_id=processed_data["author_id"], course_id=processed_data["course_id"],
            defaults = {
                'outputs': outputs,
                'metadata': processed_data["metadata"],
                'inputs': inputs,
                'analysis': analysis,
                'init_data': processed_data["init_data"],
                'date_submitted': processed_data["date_submitted"],
                'course_id': processed_data["course_id"],
                }
            )
        problem.save()
        ### finally remove previously generated executable script from disk and return success response
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        return Response("POST OK", status=status.HTTP_200_OK)


################################################ profile API endpoints ################################################

class ProfileStatsView(APIView):

    http_method_names = ['get', 'post']

    def get(self, request):
        uid = request.user.id
        try:
            problem_stats = list(Problem.objects.filter(author_id=uid).all().values(
                'metadata__difficulty',
                'metadata__category',
                'metadata__pass_threshold',
                'name',
                'date_submitted',
                'metadata__description',
                'id',
            ))

            solution_stats = list(Solution.objects.filter(submitter_id=uid).all().values(
                'analysis__scores__overall_score',
                'problem__name',
                'problem__author__user__username',
                'problem__date_submitted',
                'problem__id',
                'id',
            ))

            return Response([solution_stats, problem_stats], status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response("Ill-configured GET request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_solution(request, pk):
    try:
        Solution.objects.get(id=pk).delete()
    except Exception as e:
        return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
    return Response("DELETE OK", status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_problem(request, pk):
    try:
        Problem.objects.get(id=pk).delete()
    except Exception as e:
        return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
    return Response("DELETE OK", status=status.HTTP_200_OK)

############################################## Course API endpoints ################################################

@api_view(['POST'])
def create_course(request):
    try:
        password = request.POST.get("password", None)
        hash_obj = hashlib.sha512(password.encode('utf-8'))
        course, created = Course.objects.update_or_create(
            tutor=request.user,
            name = request.POST.get("name", None),
            defaults={'name': request.POST.get("name", None), 
                'description': request.POST.get("description", None),
                'code': request.POST.get("code", None),
                'hash_digest': hash_obj.hexdigest()
            }
        )
        course.save()
        return Response(str(course.id), status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Failure: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def enrol_course(request, course_code):
    try:
        password = request.POST.get("password", None)
        hash_obj = hashlib.sha512(password.encode('utf-8'))
        course = Course.objects.filter(code=course_code).first()
        correct_password = hash_obj.hexdigest() == course.hash_digest
        if course and correct_password:
            enrolment, created = Enrolment.objects.update_or_create(
                student=request.user,
                course = course,
                defaults={}
            )
            enrolment.save()
            return Response(str(course.id), status=status.HTTP_200_OK)
        else:
            resp = "Failure: no such course" if not course else "Failure: incorrect password" if not correct_password else ""
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response("Failure {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'DELETE'])
def delete_entity(request, del_type, del_id):
    if del_type == "problem":
        try:
            Problem.objects.get(id=del_id).delete()
        except Exception as e:
            return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return Response("DELETE OK", status=status.HTTP_200_OK)
    elif del_type == "course":
        print("Course {0} successfully deactivated".format(del_id))
        return Response("DEACTIVATION OK", status=status.HTTP_200_OK)
    else:
        return Response("Failure", status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_global_problem_stats(request, problem_id, course_id, role):
    if role == "tutor":
        valid_req = Course.objects.filter(tutor_id=request.user.id).first()
    elif role == "student":
        valid_req = Enrolment.objects.filter(student_id=request.user.id).first()
    if valid_req:
        # solutions = list(Solution.objects.filter(problem_id=problem_id).filter(course_id=course_id).all())
        solutions = list(Solution.objects.filter(problem_id=problem_id).filter(course_id=course_id).order_by('submitter_id', '-date_submitted').distinct('submitter_id'))
        stats_data = []
        for solution in solutions:
            time_res = solution.analysis.get("udef_func_time_tot", 0)
            score_res = solution.analysis.get("score", 0)
            mem_res = solution.analysis.get("total_physical_mem", 0)
            uname = solution.submitter.username
            stats_data.append({
                "score": score_res,
                "tot_time": time_res,
                "tot_mem": mem_res,
                "username": uname
                })
        return Response(stats_data, status=status.HTTP_200_OK)
    else:
        return Response("Failure", status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_course(request):
    try:
        course_code = request.GET.get("course_code", None)
        course = Course.objects.filter(code=course_code).first()
        if course:
            data = {
                "name": course.name,
                "code": course.code,
                "description": course.description,
                "tutor": course.tutor.username
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response("Failure: no such course", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response("Failure {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)