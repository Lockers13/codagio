from django.shortcuts import render, redirect
from code_analysis.models import Problem, Solution
from .models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

class ProfileStatsView(APIView):

    http_method_names = ['get', 'post']

    def get(self, request):

        uid = request.user.id

        problem_stats = list(Problem.objects.filter(author_id=uid).all().values(
            'metadata__difficulty',
            'metadata__category',
            'metadata__pass_threshold',
            'name',
            'date_submitted',
            'metadata__description',
        ))

        solution_stats = list(Solution.objects.filter(submitter_id=uid).all().values(
            'analysis__scores__overall_score',
            'problem__name',
            'problem__author__user__username',
            'problem__date_submitted',
        ))

        return Response([solution_stats, problem_stats], status=status.HTTP_200_OK)


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
