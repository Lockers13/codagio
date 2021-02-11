import os
import json
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_utils
from ca_modules.analyzer import Analyzer
from datetime import datetime
from .models import User, Problem, Solution

class SubmissionView(APIView):

    def get(self, request):
        return Response("GET OK", status=status.HTTP_200_OK)
    
    def post(self, request):
        def validate_submission(sub):
            ### mock validation function
            if not sub.startswith("def"):
                raise ValidationError(
                    _('%(sub)s is not valid code'),
                    params={'sub': sub},
                )
            return True

        data = request.data
        sub_type = data.get("sub_type")
        # Artificially create a user and problem instance
        uid = data.get("user_id")[0]
        prob_id = data.get("problem_id")[0]
        code_data = data.get("solution")
        user = User.objects.filter(id=uid).first()
        problem = Problem.objects.filter(id=prob_id).first()
        filename = "{0}.py".format(problem.name)
        if validate_submission(code_data):
            make_utils.make_file(filename, code_data)
            analyzer = Analyzer(filename)
            analyzer.visit_ast()

            if sub_type == "solution" and problem is not None:
                percentage_score = analyzer.verify(problem)
                ### only profile submission if all tests are passed
                if float(percentage_score) == 100.0:
                    analyzer.profile(problem.inputs)
                analysis = analyzer.get_prog_dict()
                solution, created = Solution.objects.update_or_create(
                    user_id=uid,
                    problem_id=prob_id,
                    defaults={'analysis': json.dumps(analysis), 'date_submitted': datetime.now()}
                )
                solution.save()

            elif sub_type == "problem":
                json_inputs = data['inputs'].read().decode("utf-8")
                analyzer.profile(json_inputs, solution=False)
                analysis = json.dumps(analyzer.get_prog_dict())
                difficulty = data['difficulty']
                name = data['name'][0]
                desc = data['desc']
                hashes = make_utils.gen_sample_hashes(filename, json_inputs)
                problem, created = Problem.objects.update_or_create(
                    id=prob_id,
                    defaults={
                        'difficulty': difficulty,
                        'hashes': json.dumps(hashes),
                        'date_created': datetime.now(),
                        'author_id': uid,
                        'desc': desc,
                        'name': problem.name,
                        'inputs': json_inputs,
                        'analysis': analysis
                    }
                )
                problem.save()

            os.remove(filename)
            return Response(analysis, status=status.HTTP_200_OK)
        else:
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)