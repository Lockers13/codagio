from django import forms


class SolutionSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.HiddenInput())

class ProblemUploadForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    program = forms.FileField()
    meta_file = forms.FileField()
    input_files = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

