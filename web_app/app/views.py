from django.shortcuts import render


def index(request):
	

	
	context = {'title': 'Codefare | Home'}

	return render(request, 'index.html', context)