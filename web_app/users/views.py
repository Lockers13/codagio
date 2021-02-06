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

class PlainTextParser(BaseParser):
    """
    Plain text parser.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()


@parser_classes([PlainTextParser])
class Submission(APIView):

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
        if bool(request.data):
            code_data = request.data.decode("utf-8")
            if self.__validate_submission(code_data):
                maker.make_file("hello.py", code_data)
                return Response("POST OK", status=status.HTTP_200_OK)
        return Response("POST NOT OK", status=status.HTTP_400_BAD_REQUEST)