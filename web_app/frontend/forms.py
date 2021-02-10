from django import forms

class StudentSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.Textarea(attrs={"rows":25, "cols":100}))
