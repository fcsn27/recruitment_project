from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


DEPARTMENTS = [
    ('IT', 'Công nghệ thông tin'),
    ('HR', 'Nhân sự'),
    ('Finance', 'Tài chính'),
    ('Marketing', 'Marketing'),
]

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu', required=True)
    department = forms.ChoiceField(choices=DEPARTMENTS, required=False, label='Phòng ban')
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True, label='Vai trò')

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'role', 'department', 'phone_number', 'address']
        labels = {
            'email': 'Email',
            'full_name': 'Họ tên',
            'phone_number': 'Số điện thoại',
            'address': 'Địa chỉ',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    department = forms.ChoiceField(choices=DEPARTMENTS, required=False, label='Phòng ban')
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True, label='Vai trò')

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'role', 'department', 'phone_number', 'address', 'is_active']
        labels = {
            'email': 'Email',
            'full_name': 'Họ tên',
            'phone_number': 'Số điện thoại',
            'address': 'Địa chỉ',
            'is_active': 'Hoạt động',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email