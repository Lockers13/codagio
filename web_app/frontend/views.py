from django.shortcuts import render
from . import forms as dummy_forms


def index(request):
    return render(request, 'frontend/index.html')

def user_sub(request):
    initial_state = {
        'user_id': 1,
        'problem_id': 1,
        'solution': "def is_prime(num):\n    for i in range(2, num):\n        if num % i == 0:\n           return False\n    return True"
    }
    form = dummy_forms.StudentSubmissionForm(initial=initial_state)
    context = {'title': 'CGC | Home',
				'form': form}
    return render(request, 'frontend/user_sub.html', context)
