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

        def gen_hashes():
            ### mock hash generation function
            return json.dumps(["dc6ec8d68b5e4c061aa348afd1197e68",
                               "4453577800c2966a64c2dbdbcb12fe4b",
                                "6a957bceecef5cbe7de952d9463bde97"])

        data = request.data
        # Artificially create a user and problem instance
        uid = data['user_id'][0]
        prob_id = data['problem_id'][0]
        code_data = data['solution']
        user = User.objects.filter(id=uid).first()
        problem = Problem.objects.filter(id=prob_id).first()
        filename = "{0}.py".format(problem.name)
        if validate_submission(code_data):
            maker.make_file(filename, code_data)
            analyzer = Analyzer(filename)
            analyzer.visit_ast()
            analysis = analyzer.get_prog_dict()

            if data.get("inputs", None) is None and problem is not None:
                percentage_score = analyzer.verify(problem)
                ### only profile submission if all tests are passed
                if float(percentage_score) == 100.0:
                    analyzer.profile(problem)

                submission = Submission(
                    user_id=user, 
                    problem_id=problem, 
                    analysis=json.dumps(analysis), 
                    date_submitted=datetime.now()
                )
                submission.save()

            elif data.get("inputs", None) is not None:
                uploaded_json = data['inputs'].read().decode("utf-8")
                difficulty = data['difficulty']
                name = data['name'][0]
                desc = data['desc']
                hashes = gen_hashes()
                problem = Problem(
                    id=prob_id,
                    difficulty=difficulty,
                    hashes=hashes,
                    date_created=datetime.now(),
                    author_id=uid,
                    desc=desc,
                    name=problem.name,
                    inputs=uploaded_json
                )
                problem.save()

            os.remove(filename)
            return Response(analysis, status=status.HTTP_200_OK)
        else:
            return Response("POST NOT OK", status=status.HTTP_400_BAD_REQUEST)


            

