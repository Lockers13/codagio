from django.shortcuts import render
from . import forms as course_forms
from .models import Course
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
# Create your views here.

def create_course_view(request):
    context = {'title': 'CGC: Code For Code\'s Sake', 'form': course_forms.CreateCourseForm}
    return render(request, 'main/create_course_view.html', context)

@api_view(['POST'])
def create_course(request):
    try:
        course, created = Course.objects.update_or_create(
            tutor=request.user,
            name = request.POST.get("name", None),
            defaults={'name': request.POST.get("name", None), 'description': request.POST.get("description", None)}
        )
        course.save()
        return Response("Success", status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Failure: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

def search_course_view(request):
    courses = list(Course.objects.all())
    context = {'title': 'CGC: Code For Code\'s Sake', 'courses': courses}
    return render(request, 'main/course_view.html', context)