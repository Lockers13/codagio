
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ROLES=[('student','Student'),
         ('tutor','Tutor')]

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
#	role = forms.ChoiceField(choices=ROLES, widget=forms.RadioSelect, required=True)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		user.role = "student" # self.cleaned_data['role']
		if commit:
			user.save()
		return user