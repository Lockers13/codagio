from django.shortcuts import render
from . import forms as course_forms
from .models import Course, Enrolment
from code_analysis.models import Problem, Solution
from django.db.models import Q
# Create your views here.

def delete_response(request, del_type, course_id):
    course = Course.objects.filter(id=course_id).first()
    de_msg ="Your problem was deleted successully!" if del_type == "problem" else "Your course was deactivated successfully!" if del_type == "course" else ""
    context = {'course': course, "de_msg": de_msg, "del_type": del_type}
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

def submission_overview(request, course_id, prob_id):
    solutions = list(Solution.objects.filter(problem_id=prob_id).order_by('submitter_id', '-date_submitted').distinct('submitter_id'))
    problem = solutions[0].problem if solutions else None
    submitter_ids = [solution.submitter_id for solution in solutions]
    other_students = [enrolment.student for enrolment in list(Enrolment.objects.filter(course_id=course_id).filter(~Q(student_id__in=submitter_ids)).all())]
    context = {'other_students': other_students, 'solutions': solutions, 'problem': problem}
    return render(request, 'courses/submission_overview.html', context)

def problem_view(request, problem_id, uid):
    which = request.GET.get('which', "latest")
    if which == "latest":
        solutions = list(Solution.objects.filter(submitter_id=uid).filter(problem_id=problem_id).all().order_by('-date_submitted'))
        solution = solutions[0] if solutions else None
        context = {'other_solutions': solutions[1:], 'problem_id': problem_id, 'solution': solution, 'latest': True}
    elif which == "other":
        soln_id = request.GET.get("soln_id", None)
        solution = Solution.objects.filter(id=soln_id).first()
        context = {'problem_id': problem_id, 'solution': solution, 'latest': False}
    return render(request, 'courses/problem_view.html', context)