from django import forms
from django.contrib.auth.models import User
from .models import CompanyInfo, InterviewSchedule
from django.db import models
from .models import InterviewSchedule, CustomUser


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
    interviewers = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='Người phỏng vấn'
    )
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Thời gian phỏng vấn'
    )

    class Meta:
        model = InterviewSchedule
        fields = ['interviewers', 'scheduled_time', 'location', 'notes']  # Sửa từ 'interviewer' thành 'interviewers'

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['interviewers'].queryset = CustomUser.objects.filter(
                models.Q(department=department, is_interviewer=True) | 
                models.Q(role='hr', is_interviewer=True)
            )

    def clean_interviewers(self):
        interviewers = self.cleaned_data['interviewers']
        # Kiểm tra có ít nhất một người từ HR
        has_hr = any(user.role == 'hr' for user in interviewers)
        if not has_hr:
            raise forms.ValidationError('Phải chọn ít nhất một người phỏng vấn từ team HR.')
        return interviewers