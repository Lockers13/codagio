from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SolutionSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.Textarea(attrs={"rows":25, "cols":100}))

class ProblemSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    desc = forms.CharField(required=False, max_length=200)
    name = forms.CharField(required=True, max_length=50)
    inputs = forms.FileField()
    difficulty = forms.CharField(required=True, max_length=20)
    solution = forms.CharField(widget=forms.Textarea(attrs={"rows":25, "cols":100}))

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class LoginForm:
    pass