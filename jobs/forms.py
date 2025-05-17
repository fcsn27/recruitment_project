from django import forms
from .models import Application, JobRequest, JobPosting

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv']

class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = ['title', 'department', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'is_active': forms.CheckboxInput(),
        }

class JobRequestForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [
        ('IT', 'Công nghệ thông tin'),
        ('HR', 'Nhân sự'),
        ('Marketing', 'Tiếp thị'),
        ('Finance', 'Tài chính'),
    ]
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select)

    class Meta:
        model = JobRequest
        fields = ['title', 'department', 'quantity', 'description', 'reason']
        widgets = {
            'title': forms.TextInput,
            'quantity': forms.NumberInput,
            'description': forms.Textarea(attrs={'rows': 4}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }