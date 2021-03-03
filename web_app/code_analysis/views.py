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

            problem = Problem.objects.filter(id=prob_id).first()
            percentage_score = analyzer.verify(problem)
            centpourcent = float(percentage_score) == 100.0
            ### only profile submission if all tests are passed
            if centpourcent:
                analyzer.profile(problem.inputs)
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
        else:
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)


def solution_upload(request, prob_id):

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    form = submission_forms.SolutionSubmissionForm(initial=initial_state)


    context = {'title': 'CGC | Home',
                'form': form}

    return render(request, 'code.html', context)
