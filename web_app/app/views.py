from django.shortcuts import render
from code_analysis.models import Problem


def index(request):
	problems = Problem.objects.all().values('name', 'desc', 'difficulty', 'author__user__username', 'date_created')

	context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems}

	return render(request, 'index.html', context)