from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Chào mừng, {user.full_name}!')
            if user.role == 'hr':
                return redirect('hr:manage_job_postings')
            elif user.role == 'department':
                return redirect('jobs:manage_job_requests')
            elif user.role == 'director':
                return redirect('jobs:manage_job_requests')
            else:
                return redirect('hr:company_info')  # Chuyển hướng ứng viên đến Về chúng tôi
        else:
            messages.error(request, 'Email hoặc mật khẩu không đúng.')
    else:
        form = AuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công.')
    return redirect('accounts:login')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # user = form.save()
                user = form.save(commit=False)
                user.role = 'applicant'  # Gán vai trò ứng viên
                user.save()
                messages.success(request, f'Tài khoản {user.email} đã được tạo thành công.')
                return redirect('accounts:login')
            except IntegrityError:
                messages.error(request, 'Email này đã được sử dụng.')
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def user_management(request):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự HR có thể quản lý người dùng.')
        return redirect('jobs:job_list')
    users = CustomUser.objects.all()
    return render(request, 'accounts/user_management.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự HR có thể chỉnh sửa người dùng.')
        return redirect('jobs:job_list')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tài khoản {user.email} đã được cập nhật thành công.')
            return redirect('accounts:user_management')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự HR có thể xóa người dùng.')
        return redirect('jobs:job_list')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Tài khoản {user.email} đã được xóa thành công.')
        return redirect('accounts:user_management')
    return render(request, 'accounts/delete_user.html', {'user': user})