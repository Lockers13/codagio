import os
from .models import Problem, Solution
from users.models import Profile
from django.shortcuts import render, redirect
from . import forms as submission_forms
from django.contrib.auth.models import User

def solution_upload(request, prob_id):
    ### get problem (and all associated metadata) from DB, and set initial state accordingly
    problem = Problem.objects.get(id = prob_id)
    metadata = problem.metadata
    difficulty = metadata['difficulty']
    description = metadata['description']
    main_signature = problem.analysis.get("main_signature", None)

    initial_state = {
        'user_id': request.user.id,
        'problem_id': prob_id,
        'solution': "",
    }

    ### load appropriate form
    form = submission_forms.SolutionSubmissionForm(initial=initial_state)

    ### set template context
    context = { 'title': 'CGC | Home',
                'form': form,
                'difficulty':difficulty,
                'problem_name':problem.name,
                'problem_desc':description,
                'main_signature': main_signature,
                }

    return render(request, 'main/code.html', context)

def problem_upload(request, problem_cat, course_id):
    ### obviously, since the user is creating a problem, there is no problem data to retrieve from DB
    ### nevertheless we minimally set the initial state of the form with the small amount of data we do have
    initial_state = {
        'author_id': request.user.id,
        'category': problem_cat,
        'course_id': course_id,
    }
    ### check the type of problem being uploaded, and load appropriate form
    if problem_cat == "default":
        form = submission_forms.DefaultProblemUploadForm(initial=initial_state)
    elif problem_cat == "file_io":
        form = submission_forms.IOProblemUploadForm(initial=initial_state)

    ### set template context
    context = { 'title': 'CGC | Home',
                'form': form,
                'cat': problem_cat,
                }

    return render(request, 'main/problem_upload.html', context)

def problem_view(request, category):
    problems = Problem.objects.filter(metadata__category__contains=category).all()
    context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems, 'category': category}
    return render(request, 'main/problem_view.html', context)