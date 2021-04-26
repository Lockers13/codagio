from django.shortcuts import render, redirect
from code_analysis.models import Problem, Solution
from .models import Profile

def delete_response(request):
    try:
        prob_id = request.GET.get("prob_id", None)
    except Exception as e:
        print(str(e))
        prob_id = None
        
    context = {'prob_id': prob_id}
    return render(request, 'profile/delete_response.html', context)

def profile(request):
    uid = request.user.id
    profiles = list(Profile.objects.filter(user_id=uid).all().values(
        'user__username',
        'user__email',
        'user__is_active',
        'about',
        'level',
    ))

    context = {
        'title': 'CGC | Home',
        'uid': uid,
        'profile': profiles[0],
    }

    return render(request, 'profile/profile_view.html', context)

def solution_view(request):
    try:
        soln_id = int(request.GET.get("soln_id"))
        prob_id = int(request.GET.get("prob_id"))
        if not (soln_id > 0 and prob_id > 0):
            return render(request, 'profile/profile_view.html')
    except Exception as e:
        print(str(e))
        return render(request, 'profile/profile_view.html')
    
    try:
        solutions = list(Solution.objects.filter(id=soln_id).all().values(
                'analysis',
                'problem__name',
                'id',
            ))
    except Exception as e:
        print("Error during db operation in users.solution_view : {0}".format(str(e)))
        return render(request, 'profile/profile_view.html')

    try:
        solution = solutions[0]
    except IndexError as ie:
        return render(request, 'profile/profile_view.html')

    context = {'solution': solution, 'prob_id': prob_id}

    return render(request, 'profile/solution_view.html', context)

def problem_view(request):
    try:
        prob_id = int(request.GET.get("prob_id"))
        if not (prob_id > 0):
            return render(request, 'profile/profile_view.html')
    except Exception as e:
        print("Exception in users.problem_view : {0}".format(str(e)))
        return render(request, 'profile/profile_view.html')
    try:
        problems = list(Problem.objects.filter(id=prob_id).all())
    except Exception as e:
        print("Error during db operation in users.problem_view : {0}".format(str(e)))
        return render(request, 'profile/profile_view.html')
        
    try:
        problem = problems[0]
    except IndexError as ie:
        print("Exception in users.problem_view : {0}".format(str(ie)))
        return render(request, 'profile/profile_view.html')
    
    context = {
        'prob_id': prob_id,
        'problem': problem,
    }

    return render(request, 'profile/problem_view.html', context)