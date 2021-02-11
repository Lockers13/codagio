from django.shortcuts import render
from . import forms as dummy_forms


def index(request):
    return render(request, 'frontend/index.html')

def user_sub(request, sub_type):
    if sub_type == "solution":
        initial_state = {
            'user_id': 2,
            'problem_id': 1,
            'solution': "def is_prime(num):\n    for i in range(2, num):\n        if num % i == 0:\n           return False\n    return True"
        }
        form = dummy_forms.SolutionSubmissionForm(initial=initial_state)

    elif sub_type == "problem":
        initial_state = {
            'user_id': 2,
            'problem_id': 1,
            'solution': "def is_prime(num):\n    lim = round(num**1/2)\n    for i in range(2, lim+1):\n        if num % i == 0:\n           return False\n    return True",
            'name': 'prime_checker',
            'desc': 'Quick Prime Checker',
            'difficulty': 'Easy'
        }

        form = dummy_forms.ProblemSubmissionForm(initial=initial_state)

    context = {'title': 'CGC | Home',
                'form': form,
                'sub_type': sub_type}

    return render(request, 'frontend/user_sub.html', context)


