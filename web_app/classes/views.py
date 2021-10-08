from django.shortcuts import render
from . import forms as course_forms
from .models import Course, Enrolment
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from code_analysis.models import Problem
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
        return Response(str(course.id), status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Failure: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)

def search_course_view(request):
    courses =[enrolment.course for enrolment in list(Enrolment.objects.filter(student=request.user).all())]
    context = {'title': 'CGC: Code For Code\'s Sake', 'courses': courses}
    return render(request, 'main/course_view.html', context)

def enrol_course(request):
    # enrolment, created = Enrolment.objects.update_or_create(
    #     student=request.user,
    #     defaults={'course': courses[0]}
    # )
    # enrolment.save()
    pass

def course_landing(request, course_id):
    problems = list(Problem.objects.filter(course_id=course_id).all())
    course = Course.objects.filter(id=course_id).first()
    context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems, 'course': course, 'user': request.user.profile}
    return render(request, 'main/course_landing.html', context)