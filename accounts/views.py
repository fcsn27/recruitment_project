from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, PasswordResetOTP
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
import random
from django.core.mail import send_mail
from .forms import CustomUserCreationFormForHR

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

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             try:
#                 # user = form.save()
#                 user = form.save(commit=False)
#                 user.role = 'applicant'  # Gán vai trò ứng viên
#                 user.save()
#                 messages.success(request, f'Tài khoản {user.email} đã được tạo thành công.')
#                 return redirect('accounts:login')
#             except IntegrityError:
#                 messages.error(request, 'Email này đã được sử dụng.')
#         else:
#             messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'accounts/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Tài khoản {user.email} đã được tạo thành công.')
                return redirect('accounts:login')
            except IntegrityError:
                messages.error(request, 'Email này đã được sử dụng.')
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# @login_required
# def user_management(request):
#     if request.user.role != 'hr':
#         messages.error(request, 'Chỉ nhân sự HR có thể quản lý người dùng.')
#         return redirect('jobs:job_list')

#     users = CustomUser.objects.all()

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save()
#                 messages.success(request, f'Tài khoản {user.email} đã được tạo thành công.')
#                 return redirect('accounts:user_management')
#             except IntegrityError:
#                 messages.error(request, 'Email này đã được sử dụng.')
#         else:
#             messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
#     else:
#         form = CustomUserCreationForm()

#     return render(request, 'accounts/user_management.html', {
#         'users': users,
#         'form': form
#     })

@login_required
def user_management(request):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự HR có thể quản lý người dùng.')
        return redirect('jobs:job_list')

    users = CustomUser.objects.all()

    if request.method == 'POST':
        form = CustomUserCreationFormForHR(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Tài khoản {user.email} đã được tạo thành công.')
                return redirect('accounts:user_management')
            except IntegrityError:
                messages.error(request, 'Email này đã được sử dụng.')
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = CustomUserCreationFormForHR()

    return render(request, 'accounts/user_management.html', {
        'users': users,
        'form': form
    })

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


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, code=otp)

            send_mail(
                subject='Mã OTP đặt lại mật khẩu',
                message=f'Mã OTP của bạn là: {otp}',
                from_email='noreply@example.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            request.session['reset_user_id'] = user.id
            return redirect('accounts:verify_otp')

        except CustomUser.DoesNotExist:
            messages.error(request, 'Email không tồn tại.')
    return render(request, 'accounts/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('reset_user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            otp_obj = PasswordResetOTP.objects.filter(user=user, code=otp).last()
            if otp_obj and otp_obj.is_valid():
                return redirect('accounts:reset_password')
            else:
                messages.error(request, 'Mã OTP không hợp lệ hoặc đã hết hạn.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Không tìm thấy người dùng.')
    return render(request, 'accounts/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password == confirm and len(password) >= 6:
            user_id = request.session.get('reset_user_id')
            user = CustomUser.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Mật khẩu đã được đặt lại. Vui lòng đăng nhập.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Mật khẩu không khớp hoặc không hợp lệ.')
    return render(request, 'accounts/reset_password.html')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Không bắt đăng nhập lại
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})