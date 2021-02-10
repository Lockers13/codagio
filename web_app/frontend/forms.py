from django import forms

class SolutionSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.Textarea(attrs={"rows":25, "cols":100}))

class ProblemSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    desc = forms.CharField(required=False, max_length=200)
    name = forms.CharField(required=True, max_length=50)
    inputs = forms.FileField()
    difficulty = forms.CharField(required=True, max_length=20)
    solution = forms.CharField(widget=forms.Textarea(attrs={"rows":25, "cols":100}))

