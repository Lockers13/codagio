from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import json
import sys
import yaml

CHOICES=[('Auto','Auto'),
         ('Custom','Custom')]

class SolutionSubmissionForm(forms.Form):
    def clean_solution(self):
        content = self.cleaned_data['solution']
        if sys.getsizeof(content) > settings.MAX_UPLOAD_SIZE_CODE_STRING:
            raise Exception("Submitted code exceeds size limit!")
        return content

    problem_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    solution = forms.CharField(widget=forms.HiddenInput())

class IOProblemUploadForm(forms.Form):
    def clean_program(self):
        content = self.cleaned_data['program']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_PROG:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content
        
    def clean_target_file(self):
        content = self.cleaned_data['target_file']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_TARGET_FILE:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_data_file(self):
        content = self.cleaned_data['data_file']
        if content is None:
            return content
        else:
            content_type = content.content_type.split('/')[0]
            if content.size > settings.MAX_UPLOAD_SIZE_DATA_FILE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_meta_file(self):
        content = self.cleaned_data['meta_file']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_META:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        try:
            content = yaml.safe_load(content.read())
        except Exception as e:
            raise Exception("Invalid YAML in meta file!")
        return content

    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    program = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    meta_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    target_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))

class DefaultProblemUploadForm(forms.Form):
    ### cleaning function for data_file goes here!!!
    def clean_data_file(self):
        content = self.cleaned_data['data_file']
        if content is None:
            return content
        else:
            content_type = content.content_type.split('/')[0]
            if content.size > settings.MAX_UPLOAD_SIZE_DATA_FILE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_program(self):
        content = self.cleaned_data['program']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_PROG:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    def clean_inputs(self):
        content = self.cleaned_data['inputs']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_INPUTS:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        try:
            content = json.loads(content.read())
            if not isinstance(content[0], list):
                raise Exception("POST NOT OK: Incorrectly formatted custom inputs!")
        except Exception as e:
            raise Exception("Invalid JSON in input file!")
        return content

    def clean_meta_file(self):
        content = self.cleaned_data['meta_file']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_META:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        try:
            content = yaml.safe_load(content.read())
        except Exception as e:
            raise Exception("Invalid YAML in meta file!")
        return content

    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    program = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    meta_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    inputs = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))

class NetworkingProblemUploadForm(forms.Form):
    def clean_data_file(self):
        content = self.cleaned_data['data_file']
        if content is None:
            return content
        else:
            content_type = content.content_type.split('/')[0]
            if content.size > settings.MAX_UPLOAD_SIZE_DATA_FILE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))

        return content
    def clean_meta_file(self):
        content = self.cleaned_data['meta_file']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_META:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        try:
            content = yaml.safe_load(content.read())
        except Exception as e:
            raise Exception("Invalid YAML in meta file!")
        return content
    
    def clean_program(self):
        content = self.cleaned_data['program']
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_PROG:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content
    
    def clean_api(self):
        pass

    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, max_length=50)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":10, "cols":20}))
    category = forms.CharField(widget=forms.HiddenInput(), required=True)
    program = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    meta_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))
