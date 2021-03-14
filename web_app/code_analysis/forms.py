from django import forms

class SolutionSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.HiddenInput())

class IOProblemUploadForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    program = forms.FileField()
    meta_file = forms.FileField()
    input_files = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'multiple': True}))

class DefaultProblemUploadForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    program = forms.FileField()
    meta_file = forms.FileField()
    category = forms.CharField(widget=forms.HiddenInput(), required=True)