import os
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_utils
from ca_modules.analyzer import Analyzer
from ca_modules import comparison
from datetime import datetime
from .models import Problem, Solution
from users.models import Profile
from django.shortcuts import render, redirect
from . import forms as submission_forms

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
        sub_type = data.get("sub_type")
        prob_name = data.get("name")
        # Artificially create a user and problem instance
        uid = request.user.id
        prob_id = data.get("problem_id")[0]
        code_data = data.get("solution")
        user = Profile.objects.filter(id=uid).first()
        filename = "{0}.py".format(prob_name)
        if validate_submission(code_data):
            make_utils.make_file(filename, code_data)
            analyzer = Analyzer(filename)
            analyzer.visit_ast()

            if sub_type == "solution":
                problem = Problem.objects.filter(id=prob_id).first()
                percentage_score = analyzer.verify(problem)
                ### only profile submission if all tests are passed
                if float(percentage_score) == 100.0:
                    analyzer.profile(problem.inputs)
                analysis = analyzer.get_prog_dict()
                comparison.write_comp(analysis, json.loads(problem.analysis))
                
                solution, created = Solution.objects.update_or_create(
                    submitter_id=uid,
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
                        'name': prob_name,
                        'inputs': json_inputs,
                        'analysis': analysis
                    }
                )
                problem.save()

            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

            return Response(analysis, status=status.HTTP_200_OK)
        else:
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)


def solution_upload(request, prob_id):


    # initial_state = {
    #     'user_id': request.user.id,
    #     'problem_id': 1,
    #     'solution': "def is_prime(num):\n    for i in range(2, num):\n        if num % i == 0:\n           return False\n    return True"
    # }

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    form = submission_forms.SolutionSubmissionForm(initial=initial_state)


    context = {'title': 'CGC | Home',
                'form': form,
                'sub_type': "solution"}

    return render(request, 'solution.html', context)


def problem_upload(request):

    # initial_state = {
    #     'user_id': request.user.id,
    #     'problem_id': 1,
    #     'solution': "def is_prime(num):\n    lim = round(num**1/2)\n    for i in range(2, lim+1):\n        if num % i == 0:\n           return False\n    return True",
    #     'name': 'prime_checker',
    #     'desc': 'Quick Prime Checker',
    #     'difficulty': 'Easy'
    # }

    initial_state = {
        'user_id': request.user.id,
        'problem_id': 3,
        'solution': "ABC_LOWER = 'abcdefghijklmnopqrstuvwxyz'\nABC_UPPER = ABC_LOWER.upper()\n\ndef rot13(phrase):\n" +
            "    out_phrase = \"\"\n    for char in phrase:\n        if char.isupper():\n            out_phrase += ABC_UPPER[(ABC_UPPER.find(char)+13)%26]\n" +
                "        else:\n            out_phrase += ABC_LOWER[(ABC_LOWER.find(char)+13)%26]\n    return out_phrase",
        'name': 'rot13',
        'desc': 'Rot 13 Cipher Algorithm',
        'difficulty': 'Medium'
    }

    form = submission_forms.ProblemSubmissionForm(initial=initial_state)

    context = {'title': 'CGC | Home',
        'form': form,
        'sub_type': "problem"}

    return render(request, 'solution.html', context)