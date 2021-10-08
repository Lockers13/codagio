from django.shortcuts import render
from code_analysis.models import Problem
import json

def index(request):
	problems = list(Problem.objects.all().values('name','metadata', 'author__username', 'id'))
	### turn inner json dict into python dict before passing to template
	context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems}
	return render(request, 'main/index.html', context)

def about(request):
	return render(request, 'main/about.html')