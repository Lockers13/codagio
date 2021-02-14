from django.shortcuts import render, redirect
from . import forms as dummy_forms
from .forms import NewUserForm
from django.contrib.auth import authenticate, login
from django.contrib import messages


def index(request):
    return render(request, 'frontend/index.html')

def user_sub(request, sub_type):
    if sub_type == "solution":

        # initial_state = {
        #     'user_id': 2,
        #     'problem_id': 1,
        #     'solution': "def is_prime(num):\n    for i in range(2, num):\n        if num % i == 0:\n           return False\n    return True"
        # }

        initial_state = {
            'user_id': 1,
            'problem_id': 3,
            'solution': "def rot13(phrase):\n    ascii_lower = (97, 122)\n    ascii_upper = (65, 90)\n    LEN_ALPHA = 26\n    new_string = \"\"\n" +
                "    for char in phrase:\n        ascii_num = ord(char)\n        if ascii_num >= ascii_lower[0] and ascii_num <= ascii_lower[1]:\n            if ((ascii_num - ascii_lower[0]) + 13) >= LEN_ALPHA:\n                ascii_num = ascii_lower[0] + (((ascii_num - ascii_lower[0]) + 13) - LEN_ALPHA)\n" +
                    "            else:\n                ascii_num += 13\n        elif ascii_num >= ascii_upper[0] and ascii_num <= ascii_upper[1]:\n            if ((ascii_num - ascii_upper[0]) + 13) >= LEN_ALPHA:\n" +
                        "                ascii_num = ascii_upper[0] + (((ascii_num - ascii_upper[0]) + 13) - LEN_ALPHA)\n            else:\n                ascii_num += 13\n        else:\n            pass\n" +
                            "        new_string += chr(ascii_num)\n    return new_string",
        }
        form = dummy_forms.SolutionSubmissionForm(initial=initial_state)

    elif sub_type == "problem":

        # initial_state = {
        #     'user_id': 2,
        #     'problem_id': 1,
        #     'solution': "def is_prime(num):\n    lim = round(num**1/2)\n    for i in range(2, lim+1):\n        if num % i == 0:\n           return False\n    return True",
        #     'name': 'prime_checker',
        #     'desc': 'Quick Prime Checker',
        #     'difficulty': 'Easy'
        # }

        initial_state = {
            'user_id': 1,
            'problem_id': 3,
            'solution': "ABC_LOWER = 'abcdefghijklmnopqrstuvwxyz'\nABC_UPPER = ABC_LOWER.upper()\n\ndef rot13(phrase):\n" +
                "    out_phrase = \"\"\n    for char in phrase:\n        if char.isupper():\n            out_phrase += ABC_UPPER[(ABC_UPPER.find(char)+13)%26]\n" +
                    "        else:\n            out_phrase += ABC_LOWER[(ABC_LOWER.find(char)+13)%26]\n    return out_phrase",
            'name': 'rot13',
            'desc': 'Rot 13 Cipher Algorithm',
            'difficulty': 'Medium'
        }
        form = dummy_forms.ProblemSubmissionForm(initial=initial_state)

    context = {'title': 'CGC | Home',
                'form': form,
                'sub_type': sub_type}

    return render(request, 'frontend/user_sub.html', context)


def register(request):
    print(vars(request))
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(index)
        messages.error(request, "Unsuccessful registration. Invalid information.")
        print("YO")
    form = NewUserForm
    return render(request, 'registration/register.html', context={"register_form":form})
