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
        prob_id = data.get("problem_id")[0]
        problem = Problem.objects.filter(id=prob_id).first()
        prob_name = problem.name
        # Artificially create a user and problem instance
        uid = request.user.id
        
        code_data = data.get("solution")
        user = Profile.objects.filter(id=uid).first()
        filename = "{0}.py".format(prob_name)
        if not validate_submission(code_data):
            return Response("POST NOT OK: invalid code!", status=status.HTTP_400_BAD_REQUEST)
        ### make basic initial file from code_data for the sole purposes of ast parsing
        with open(filename, 'w') as f:
            f.write(code_data)
        metadata = {
            "allowed_abs_imports": ["math"],
            "allowed_rel_imports": {
                "os": ["listdir", "chdir"]
                },
            "disallowed_fcalls": ["print", "eval"]
        }
        analyzer = Analyzer(filename, metadata)
        analyzer.visit_ast()
        ### if the ast_visitor has picked up on any blacklisted imports/functions then return appropriate error status
        if len(analyzer.get_prog_dict()["UNSAFE"]) > 0:
            os.remove(filename)
            return Response("POST NOT OK: potentially unsafe code!", status=status.HTTP_400_BAD_REQUEST)
        ### remove old basic file and create more sophisticated one for verification and profiling
        os.remove(filename)
        make_utils.make_file(filename, code_data)

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


def solution_upload(request, prob_id):

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    form = submission_forms.SolutionSubmissionForm(initial=initial_state)


    context = {'title': 'CGC | Home',
                'form': form}

    return render(request, 'solution.html', context)
