from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import UploadFileForm
from rest_framework.parsers import BaseParser
from rest_framework.decorators import parser_classes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ca_modules import make_executable as maker
from ca_modules.analyzer import Analyzer
import os
import json
from datetime import datetime
from .models import User, Problem, Submission

class SubmissionView(APIView):

    def __validate_submission(self, sub):
        ### mock validation function

        if not sub.startswith("def"):
            raise ValidationError(
                _('%(sub)s is not valid code'),
                params={'sub': sub},
            )
        return True

    def get(self, request):
        return Response("GET OK", status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        # Artificially create a user and problem instance
        uid = data['user_id'][0]
        prob_id = data['problem_id'][0]

        user = User.objects.filter(id=uid).first()
        problem = Problem.objects.filter(id=prob_id).first()

        if bool(request.data):
            code_data = data['solution']

            if self.__validate_submission(code_data):

                filename = "{0}.py".format(problem.name)
                maker.make_file(filename, code_data)
                analyzer = Analyzer(filename)
                analyzer.visit_ast()
                percentage_score = analyzer.verify(problem)
                ### only profile submission if all tests are passed
                if float(percentage_score) == 100.0:
                    analyzer.profile(problem)

                os.remove(filename)
                analysis = analyzer.get_prog_dict()
                submission = Submission(
                    user_id=user, 
                    problem_id=problem, 
                    analysis=json.dumps(analysis), 
                    date_submitted=datetime.now()
                )
                submission.save()
                return Response(analysis, status=status.HTTP_200_OK)

        return Response("POST NOT OK", status=status.HTTP_400_BAD_REQUEST)