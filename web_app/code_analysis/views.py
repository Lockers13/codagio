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

    def get(self, request):
        return Response("GET OK", status=status.HTTP_200_OK)
    
    def post(self, request):
        def validate_submission(sub):
            ### mock validation function
            if not sub:
                raise ValidationError(
                    _('%(sub)s is not valid code'),
                    params={'sub': sub},
                )
            return True

        data = request.data
        prob_id = int(data.get("problem_id"))
        problem = Problem.objects.filter(id=prob_id).first()
        prob_name = problem.name
        uid = request.user.id
        code_data = data.get("solution")
        user = Profile.objects.filter(id=uid).first()
        filename = "{0}.py".format(prob_name)
        if not validate_submission(code_data):
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'w') as f:
            f.write(code_data)
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
        if validation_result != True:
            return validation_result
        make_utils.make_file(filename, code_data)
        try:
            percentage_score = analyzer.verify(problem)
        except Exception as e:
            return Response("POST NOT OK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        centpourcent = float(percentage_score) == 100.0
        ### only profile submission if all tests are passed
        if centpourcent:
            try:
                analyzer.profile(problem.inputs)
            except Exception as e:
                return Response("POST NOT OKKK: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
        analysis = analyzer.get_prog_dict()
        comparison.write_comp(analysis, json.loads(problem.analysis))
        if centpourcent:
            solution, created = Solution.objects.update_or_create(
                submitter_id=uid,
                problem_id=prob_id,
                defaults={'analysis': json.dumps(analysis), 'date_submitted': datetime.now()}
            )
            solution.save()

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

        return Response(json.dumps(analysis), status=status.HTTP_200_OK)

class SaveProblemView(APIView):

    def get(self, request):
        return Response("GET OK", status=status.HTTP_200_OK)
    
    def post(self, request):

        data = request.data
        metadata = {}
        author_id = int(data.get("author_id"))
        author = User.objects.filter(id=author_id).first()

        if not author.is_superuser:
            print("Sorry, only admins can submit problems, exiting...")
            return Response("POST NOT OK: problem author is not superuser!", status=status.HTTP_400_BAD_REQUEST)
        name = data.get("name")
        description = data.get("description")
        meta_file = data.get("meta_file")
        program_file = data.get("program")
        metadata = yaml.full_load(meta_file.read())
        metadata["description"] = description
        metadata["date_created"] = datetime.now()
        input_type = metadata["input_type"]
        input_length = metadata["input_length"]
        num_tests = metadata["num_tests"]
        code = [line.decode("utf-8") for line in program_file.read().splitlines()]
        filename = "{0}.py".format(name)
        make_utils.make_file(filename, code, source="file")
        analyzer = Analyzer(filename, metadata)
        analyzer.visit_ast()
        json_inputs = make_utils.generate_input(input_type, input_length, num_tests)
        analyzer.profile(json_inputs, solution=False)
        analysis = json.dumps(analyzer.get_prog_dict())
        hashes = make_utils.gen_sample_hashes(filename, json_inputs)
        problem, created = Problem.objects.update_or_create(
            name=name, author_id=author_id,
            defaults = {
                'hashes': json.dumps(hashes),
                'metadata': json.dumps(metadata, default=str),
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

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
        'problem_name':problem.name,
        #'problem_desc':problem.desc,
    }

    form = submission_forms.SolutionSubmissionForm(initial=initial_state)


    context = { 'title': 'CGC | Home',
                'form': form,
                'problem_name':problem.name
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

