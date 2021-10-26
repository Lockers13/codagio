from django import forms

class CreateCourseForm(forms.Form):
    tutor = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    code = forms.CharField(max_length=15, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput())

class EnrolCourseForm(forms.Form):
    code = forms.CharField(max_length=15, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput())
