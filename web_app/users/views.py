from django.shortcuts import render, redirect
from code_analysis.models import Problem, Solution
from .models import Profile

def profile(request):
    uid = request.user.id

    problems_uploaded = list(Problem.objects.filter(author_id=uid).all().values(
        'metadata__difficulty',
        'metadata__category',
        'metadata__pass_threshold',
        'name',
        'date_submitted',
        'metadata__description',
    ))

    solutions_saved = list(Solution.objects.filter(submitter_id=uid).all().values(
        'analysis__scores__overall_score',
        'problem__name',
        'problem__author__user__username',
        'problem__date_submitted',
    ))

    context = {
        'title': 'CGC | Home',
        'uid': uid,
        'solutions_saved': solutions_saved,
        'problems_uploaded': problems_uploaded,
    }

    return render(request, 'profile.html', context)
