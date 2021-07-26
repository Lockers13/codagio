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

class BaseProblemUploadForm(forms.Form):
    def clean_inputs(self):
        content = self.cleaned_data['inputs']
        if content is None:
            return None
        content_type = content.content_type.split('/')[0]
        if content.size > settings.MAX_UPLOAD_SIZE_INPUTS:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        content = json.loads(content.read())
        if not isinstance(content, list):
                raise Exception("POST NOT OK: Incorrectly formatted custom inputs!")
        if not isinstance(content[0], list):
            if len(content) > 10:
                raise Exception("POST NOT OK: Simple input list too long!")
        else:
            if len(content) > 3:
                raise Exception("POST NOT OK: Nested iterative input list too long!")
            else:
                total_len = sum([len(x) for x in content])
                if total_len > 5000:
                    raise Exception("POST NOT OK: Too many inputs in list elements!")
        return content

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
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))

class IOProblemUploadForm(BaseProblemUploadForm):
    target_file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))

class DefaultProblemUploadForm(BaseProblemUploadForm):
    inputs = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'style':'display:block;margin-top:20px;', 'class':'form-control-sm'}))