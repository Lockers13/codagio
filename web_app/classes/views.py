from django.shortcuts import render
from . import forms as course_forms
from .models import Course, Enrolment
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from code_analysis.models import Problem
# Create your views here.

# def create_course_view(request):
#     context = {'title': 'CGC: Code For Code\'s Sake', 'form': course_forms.CreateCourseForm}
#     return render(request, 'main/create_course_view.html', context)

def delete_response(request, del_type, course_id):
    if del_type == "problem":
        course = Course.objects.filter(id=course_id).first()
        context = {'course': course, "del_type": del_type}
        return render(request, 'courses/delete_response.html', context)

def search_course_view(request, user_role):
    if user_role == "student":
        courses = [enrolment.course for enrolment in list(Enrolment.objects.filter(student=request.user).all())]
        context = {'title': 'CGC: Code For Code\'s Sake', 'courses': courses, 'form': course_forms.EnrolCourseForm}
        return render(request, 'courses/course_view.html', context)
    elif user_role == "tutor":
        courses = list(Course.objects.filter(tutor_id=request.user.id).all())
        context = {'title': 'CGC: Code For Code\'s Sake', 'courses': courses, 'form': course_forms.CreateCourseForm}
        return render(request, 'courses/course_view.html', context)
    
def course_landing(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    problems = list(Problem.objects.filter(course_id=course.id).all())
    context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems, 'course': course, 'user': request.user}
    return render(request, 'courses/course_landing.html', context)