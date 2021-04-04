from django import forms

CHOICES=[('Auto','Auto'),
         ('Custom','Custom')]

class SolutionSubmissionForm(forms.Form):
    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.HiddenInput())

class IOProblemUploadForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    program = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    meta_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    target_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm', 'multiple': True}))
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))

class DefaultProblemUploadForm(forms.Form):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    program = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    meta_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    inputs = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))