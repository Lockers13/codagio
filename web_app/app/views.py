from django.shortcuts import render
from code_analysis.models import Problem
import json

def extract_pertinent_fields(queryset, hash=True):
	problems = {}
	count = 1
	for q in queryset:
		problems["{0}".format(count)] = {}
		p_dict = problems["{0}".format(count)]
		meta = json.loads(q.get("metadata"))
		p_dict["difficulty"] = meta["difficulty"]
		p_dict["description"] = meta["description"]
		p_dict["date_created"] = meta["date_created"]
		p_dict["id"] = q.get("id")
		p_dict["author"] = q.get("author__user__username")
		p_dict["name"] = q.get("name")
		count += 1
	return problems.values()

def index(request):
	problems = Problem.objects.all().values('name', 'metadata', 'author__user__username', 'id')
	problems = extract_pertinent_fields(problems)
	context = {'title': 'CGC: Code For Code\'s Sake', 'problems': problems}
	return render(request, 'index.html', context)