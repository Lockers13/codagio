from django.shortcuts import render
from users import forms as user_forms

def index(request):
	
	form = user_forms.UploadFileForm(initial={'title': 'C_level1'})
	
	context = {'title': 'Codefare | Home',
				'form': form}

	return render(request, 'index.html', context)