from django.shortcuts import render, redirect
from code_analysis.models import Problem, Solution
from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.decorators import api_view

def delete_response(request):
    prob_id = request.GET.get("prob_id")
    context = {'prob_id': prob_id}
    return render(request, 'delete_response.html', context)

@api_view(['DELETE'])
def delete_solution(request, pk):
    try:
        Solution.objects.get(id=pk).delete()
    except Exception as e:
        return Response("Ill-configured DELETE request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
    return Response("DELETE OK", status=status.HTTP_200_OK)

class ProfileStatsView(APIView):

    http_method_names = ['get', 'post']

    def get(self, request, spec):
        uid = request.user.id

        try:
            spec = int(spec)
            if spec == 0:
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
            else:
                return Response("Ill-configured GET request: {0}".format(str(e)), status=status.HTTP_400_BAD_REQUEST)
                
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

    return render(request, 'profile.html', context)
