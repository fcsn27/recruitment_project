from django import forms
from django.contrib.auth.models import User
from .models import CompanyInfo, InterviewSchedule


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['name', 'description', 'address', 'website', 'email', 'phone', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên công ty',
            'description': 'Mô tả',
            'address': 'Địa chỉ',
            'website': 'Website',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'logo': 'Logo công ty',
        }


class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = InterviewSchedule
        fields = ['interviewers', 'scheduled_time', 'location', 'notes']

    def __init__(self, *args, interviewer_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if interviewer_queryset is not None:
            self.fields['interviewer'].queryset = interviewer_queryset