from django.shortcuts import render
from . import forms as course_forms

# Create your views here.

def create_course_view(request):
    context = {'title': 'CGC: Code For Code\'s Sake', 'form': course_forms.CreateCourseForm}
    return render(request, 'main/create_course_view.html', context)

def search_course_view():
    pass