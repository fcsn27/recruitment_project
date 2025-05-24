from django import forms
from .models import Application, JobRequest, JobPosting

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv']


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'is_active': forms.CheckboxInput(),
        }

class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = ['title', 'quantity', 'description', 'reason']
        labels = {
            'title': 'Vị trí tuyển dụng',
            'quantity': 'Số lượng',
            'description': 'Mô tả',
            'reason': 'Lý do',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
            }),
            'reason': forms.Textarea(attrs={
                'rows': 1,
                'class': 'form-control',
            }),
        }