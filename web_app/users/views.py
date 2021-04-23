from django.shortcuts import render, redirect
from code_analysis.models import Problem, Solution
from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.decorators import api_view

def delete_response(request):
    try:
        prob_id = request.GET.get("prob_id", None)
    except Exception as e:
        print(str(e))
        prob_id = None
        
    context = {'prob_id': prob_id}
    return render(request, 'profile_view/delete_response.html', context)

@api_view(['DELETE'])
def delete_solution(request, pk):
    try:
        Solution.objects.get(id=pk).delete()
    except Exception as e:
        return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
    return Response("DELETE OK", status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_problem(request, pk):
    try:
        Problem.objects.get(id=pk).delete()
    except Exception as e:
        return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
    return Response("DELETE OK", status=status.HTTP_200_OK)

class ProfileStatsView(APIView):

    http_method_names = ['get', 'post']

    def get(self, request):
        uid = request.user.id
        try:
            problem_stats = list(Problem.objects.filter(author_id=uid).all().values(
                'metadata__difficulty',
                'metadata__category',
                'metadata__pass_threshold',
                'name',
                'date_submitted',
                'metadata__description',
                'id',
            ))

            solution_stats = list(Solution.objects.filter(submitter_id=uid).all().values(
                'analysis__scores__overall_score',
                'problem__name',
                'problem__author__user__username',
                'problem__date_submitted',
                'problem__id',
                'id',
            ))

            return Response([solution_stats, problem_stats], status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response("Ill-configured GET request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)


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

    return render(request, 'profile_view/profile.html', context)

def solution_view(request):
    try:
        soln_id = int(request.GET.get("soln_id"))
        prob_id = int(request.GET.get("prob_id"))
        if not (soln_id > 0 and prob_id > 0):
            return render(request, 'profile_view/profile.html')
    except Exception as e:
        print(str(e))
        return render(request, 'profile_view/profile.html')
    
    try:
        solutions = list(Solution.objects.filter(id=soln_id).all().values(
                'analysis',
                'problem__name',
                'id',
            ))
    except Exception as e:
        print("Error during db operation in users.solution_view : {0}".format(str(e)))
        return render(request, 'profile_view/profile.html')

    try:
        solution = solutions[0]
    except IndexError as ie:
        return render(request, 'profile_view/profile.html')

    context = {'solution': solution, 'prob_id': prob_id}

    return render(request, 'profile_view/solution_view.html', context)

def problem_view(request):
    try:
        prob_id = int(request.GET.get("prob_id"))
        if not (prob_id > 0):
            return render(request, 'profile_view/profile.html')
    except Exception as e:
        print("Exception in users.problem_view : {0}".format(str(e)))
        return render(request, 'profile_view/profile.html')
    try:
        problems = list(Problem.objects.filter(id=prob_id).all())
    except Exception as e:
        print("Error during db operation in users.problem_view : {0}".format(str(e)))
        return render(request, 'profile_view/profile.html')
        
    ### turn inner json dict into python dict before passing to template
    try:
        problem = problems[0]
    except IndexError as ie:
        print("Exception in users.problem_view : {0}".format(str(ie)))
        return render(request, 'profile_view/profile.html')
    
    context = {
        'prob_id': prob_id,
        'problem': problem,
    }

    return render(request, 'profile_view/problem_view.html', context)