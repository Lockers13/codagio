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
from code_analysis.models import Problem
from django.contrib.auth.models import User
import yaml

class AnalysisView(APIView):

    http_method_names = ['post']

    def __process_request_data(self, request):
        processed_data = {}
        try:
            processed_data["prob_id"] = int(request.data.get("problem_id"))
            processed_data["uid"] = request.user.id
            processed_data["code_data"] = request.data.get("solution")
        except Exception as e:
            return Response("POST NOT OK: Error during intial processing of uploaded data - {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        return processed_data

    def post(self, request):
        def validate_submission(sub):
            ### mock validation function
            if not sub:
                raise ValidationError(
                    _('%(sub)s is not valid code'),
                    params={'sub': sub},
                )
            return True


        processed_data = self.__process_request_data(request)
        if isinstance(processed_data, Response):
            return processed_data
        try:
            problem = Problem.objects.filter(id=processed_data["prob_id"]).first()
        except Exception as e:
            return Response("POST NOT OK: reference problem db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        prob_name = problem.name

        try:
            user = Profile.objects.filter(id=processed_data["uid"]).first()
        except Exception as e:
            return Response("POST NOT OK: uid db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        filename = "{0}.py".format(prob_name)

        if not validate_submission(processed_data["code_data"]):
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'w') as f:
            f.write(processed_data["code_data"])
        metadata = json.loads(problem.metadata)
        analyzer = Analyzer(filename, metadata)
        try:
            analyzer.visit_ast()
        except Exception as e:
            os.remove(filename)
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### if the ast_visitor has picked up on any blacklisted imports/functions then return appropriate error status
        ast_analysis = analyzer.get_prog_dict()
        validation_result = ast_checker.validate(ast_analysis, filename)
        if isinstance(validation_result, Response):
            return validation_result
        make_utils.make_file(filename, processed_data["code_data"])
        try:
            percentage_score = analyzer.verify(problem)
        except Exception as e:
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        hundred_pc = float(percentage_score) == 100.0
        ### only profile submission if all tests are passed
        if hundred_pc:
            try:
                analyzer.profile(problem.inputs)
            except Exception as e:
                return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        analysis = analyzer.get_prog_dict()
        comparison.write_comp(analysis, json.loads(problem.analysis))
        if hundred_pc:
            solution, created = Solution.objects.update_or_create(
                submitter_id=processed_data["uid"],
                problem_id=processed_data["prob_id"],
                defaults={'analysis': json.dumps(analysis), 'date_submitted': datetime.now()}
            )
            solution.save()

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

        return Response(json.dumps(analysis), status=status.HTTP_200_OK)

class SaveProblemView(APIView):
    """Class based API view for handling the submission of a reference problem"""

    http_method_names = ['post']

    def __process_request_data(self, data):
        processed_data = {}
        try:
            processed_data["author_id"] = int(data.get("author_id"))
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

        data = request.data
        processed_data = self.__process_request_data(data)
        if isinstance(processed_data, Response):
            return processed_data
        try:
            author = User.objects.filter(id=processed_data.get("author_id")).first()
            if not author.is_superuser:
                return Response("POST NOT OK: problem author is not superuser!", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("POST NOT OK: author db exception = {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

        filename = "{0}.py".format(processed_data["name"])
        input_type = processed_data["metadata"]["input_type"]
        input_length = processed_data["metadata"]["input_length"]
        num_tests = processed_data["metadata"]["num_tests"]
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'wb+') as f:
            for chunk in processed_data["program_file"].chunks():
                f.write(chunk)
        analyzer = Analyzer(filename, processed_data["metadata"])
        try:
            analyzer.visit_ast()
        except Exception as e:
            os.remove(filename)
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        ### if the ast_visitor has picked up on any blacklisted imports/functions then return appropriate error status
        ast_analysis = analyzer.get_prog_dict()
        validation_result = ast_checker.validate(ast_analysis, filename)
        if isinstance(validation_result, Response):
            return validation_result

        make_utils.make_file(filename, processed_data["code"], source="file")
        json_inputs = make_utils.generate_input(input_type, input_length, num_tests)
        analyzer.profile(json_inputs, solution=False)
        analysis = json.dumps(analyzer.get_prog_dict())
        hashes = make_utils.gen_sample_hashes(filename, json_inputs)
        problem, created = Problem.objects.update_or_create(
            name=processed_data["name"], author_id=processed_data["author_id"],
            defaults = {
                'hashes': json.dumps(hashes),
                'metadata': json.dumps(processed_data["metadata"], default=str),
                'inputs': json_inputs,
                'analysis': analysis
                }
            )

        problem.save()

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        return Response("POST OK", status=status.HTTP_200_OK)


def solution_upload(request, prob_id):

    problem = Problem.objects.get(id = prob_id)
    metadata = json.loads(problem.metadata)
    difficulty = metadata['difficulty']
    description = metadata['description']

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    form = submission_forms.SolutionSubmissionForm(initial=initial_state)


    context = { 'title': 'CGC | Home',
                'form': form,
                'difficulty':difficulty,
                'problem_name':problem.name,
                'problem_desc':description,
                }

    return render(request, 'code.html', context)

def problem_upload(request):

    initial_state = {
        'author_id': request.user.id,
        'name': 'prime_checker',
    }

    form = submission_forms.ProblemUploadForm(initial=initial_state)


    context = { 'title': 'CGC | Home',
                'form': form,
                }

    return render(request, 'problem_upload.html', context)