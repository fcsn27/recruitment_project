from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from jobs.models import JobPosting, Application, ActionLog, JobRequest
from .models import CompanyInfo, InterviewSchedule
from .forms import CompanyInfoForm, InterviewScheduleForm
from jobs.forms import JobPostingForm
from accounts.models import CustomUser
from django.utils import timezone
from django.db.models import Count

@login_required
def manage_job_postings(request):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can manage job postings.')
        return redirect('jobs:job_list')
    job_postings = JobPosting.objects.all()
    return render(request, 'hr/manage_job_postings.html', {'job_postings': job_postings})

@login_required
def create_job_posting(request):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can create job postings.')
        return redirect('jobs:job_list')
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.created_by = request.user
            job_posting.save()
            messages.success(request, 'Job posting created successfully.')
            return redirect('hr:manage_job_postings')
    else:
        form = JobPostingForm()
    return render(request, 'hr/create_job_posting.html', {'form': form})

@login_required
def edit_job_posting(request, job_id):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can edit job postings.')
        return redirect('jobs:job_list')
    job_posting = get_object_or_404(JobPosting, id=job_id)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job posting "{job_posting.title}" updated successfully.')
            return redirect('hr:manage_job_postings')
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'hr/edit_job_posting.html', {'form': form, 'job_posting': job_posting})

@login_required
def delete_job_posting(request, job_id):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can delete job postings.')
        return redirect('jobs:job_list')
    job_posting = get_object_or_404(JobPosting, id=job_id)
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, f'Job posting "{job_posting.title}" deleted successfully.')
        return redirect('hr:manage_job_postings')
    return redirect('hr:manage_job_postings')

@login_required
@login_required
def manage_applications(request):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ bộ phận nhân sự mới được phép quản lý đơn ứng tuyển.')
        return redirect('jobs:job_list')
    
    applications = Application.objects.all()
    return render(request, 'hr/manage_applications.html', {'applications': applications})

# @login_required
# def update_application_status(request, application_id):
#     if request.user.role != 'hr':
#         messages.error(request, 'Chỉ bộ phận nhân sự mới được cập nhật trạng thái đơn ứng tuyển.')
#         return redirect('hr:application_status')

#     application = get_object_or_404(Application, id=application_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')

#         allowed_transitions = {
#             'approved': ['passed', 'rejected'],
#             # Có thể mở rộng thêm trạng thái khác nếu cần
#         }

#         current_status = application.status

#         # Chỉ cho phép thay đổi trạng thái theo quy tắc
#         if current_status not in allowed_transitions or new_status not in allowed_transitions.get(current_status, []):
#             messages.error(request, 'Trạng thái không hợp lệ hoặc không được phép thay đổi.')
#             return redirect('hr:application_status')

#         if new_status == 'rejected':
#             application.delete()
#             messages.success(request, 'Đơn ứng tuyển đã bị từ chối và xóa khỏi hệ thống.')
#             return redirect('hr:application_status')

#         application.status = new_status
#         application.save()

#         ActionLog.objects.create(
#             user=request.user,
#             action_type='update_application_status',
#             job_request=None,
#             details=f'Cập nhật trạng thái đơn {application.id} từ {current_status} sang {new_status}',
#             timestamp=timezone.now()
#         )

#         messages.success(request, f'Đơn ứng tuyển đã được cập nhật trạng thái: {new_status}.')

#         return redirect('hr:application_status')

#     return redirect('hr:application_status')

@login_required
def update_application_status(request, application_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự mới được cập nhật trạng thái.')
        return redirect('hr:manage_applications')

    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', 'Không phù hợp với tiêu chí ứng tuyển')

        if status not in ['pending', 'accepted', 'rejected']:
            messages.error(request, 'Trạng thái không hợp lệ.')
            return redirect('hr:manage_applications')

        application.status = status

        if status == 'rejected':
            application.rejection_reason = rejection_reason
        else:
            application.rejection_reason = None  # Xóa lý do khi không bị từ chối

        application.save()

        # Ghi log nếu cần
        ActionLog.objects.create(
            user=request.user,
            action_type='update_application_status',
            details=f"Cập nhật đơn {application.id} sang trạng thái {status}" + (f", lý do từ chối: {rejection_reason}" if status == 'rejected' else ""),
            timestamp=timezone.now()
        )

        messages.success(request, 'Cập nhật trạng thái đơn ứng tuyển thành công.')
        return redirect('hr:manage_applications')
    else:
        return redirect('hr:manage_applications')


@login_required
def recruitment_history(request):
    if request.user.role not in ['hr', 'director']:
        messages.error(request, 'Only HR and directors can view recruitment history.')
        return redirect('jobs:job_list')
    logs = ActionLog.objects.all().order_by('-timestamp')
    return render(request, 'hr/history.html', {'logs': logs})

@login_required
def manage_company_info(request):
    if request.user.role != 'hr':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('jobs:job_list')
    company_info = CompanyInfo.objects.first()
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, request.FILES, instance=company_info)
        if form.is_valid():
            company_info = form.save(commit=False)
            company_info.updated_by = request.user
            company_info.save()
            messages.success(request, 'Thông tin doanh nghiệp đã được cập nhật.')
            return redirect('hr:manage_company_info')
    else:
        form = CompanyInfoForm(instance=company_info)
    return render(request, 'hr/manage_company_info.html', {'form': form})

# @login_required
# def application_status(request):
#     user = request.user
#     if user.role == 'hr':
#         applications = Application.objects.all()
#     elif user.role == 'department':
#         applications = Application.objects.filter(job__department=user.department)
#     else:  # ứng viên
#         applications = Application.objects.filter(user=user)
#     return render(request, 'hr/application_status.html', {'applications': applications})

@login_required
def application_status(request):
    user = request.user
    if user.role == 'applicant':
        applications = Application.objects.filter(user=user)
    elif user.role == 'department':
        applications = Application.objects.filter(job__department=user.department)
    elif user.role == 'hr':
        applications = Application.objects.all()
    else:
        applications = Application.objects.none()
    
    return render(request, 'hr/application_status.html', {'applications': applications})

# @login_required
# def schedule_interview(request, application_id):
#     user = request.user

#     # Kiểm tra role: chỉ HR hoặc department mới được lên lịch
#     # if user.role not in ['hr', 'department']:
#     #     messages.error(request, 'Chỉ bộ phận nhân sự và trưởng phòng ban mới được lên lịch phỏng vấn.')
#     #     return redirect('jobs:job_list')
#     if user.role != 'hr':
#         messages.error(request, 'Chỉ bộ phận nhân sự mới được phép lên lịch phỏng vấn.')
#         return redirect('jobs:job_list')

#     application = get_object_or_404(Application, id=application_id)
#     job = application.job

#     # Nếu là trưởng phòng ban, kiểm tra vị trí tuyển dụng thuộc phòng của họ
#     if user.role == 'department':
#         if job.department != user.department:
#             messages.error(request, 'Bạn chỉ được lên lịch phỏng vấn cho các vị trí thuộc phòng ban của bạn.')
#             return redirect('hr:manage_applications')

#     # Xử lý form lên lịch phỏng vấn
#     if request.method == 'POST':
#         form = InterviewScheduleForm(request.POST)
#         if form.is_valid():
#             interview = form.save(commit=False)
#             interview.created_by = user
#             interview.application = application  # gán liên kết ứng dụng
#             interview.save()
#             messages.success(request, 'Lịch phỏng vấn đã được tạo thành công.')
#             return redirect('hr:manage_applications')
#     else:
#         form = InterviewScheduleForm(initial={'application': application})

#     return render(request, 'hr/schedule_interview.html', {'form': form, 'application': application})

@login_required
def schedule_interview(request, application_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ bộ phận nhân sự mới được phép lên lịch phỏng vấn.')
        return redirect('hr:manage_applications')

    application = get_object_or_404(Application, id=application_id)
    job = application.job
    department = job.department

    print(f"Application ID: {application_id}")
    print(f"Job department: {department}")

    if not department:
        messages.error(request, 'Vị trí tuyển dụng này chưa được gán phòng ban.')
        return redirect('hr:manage_applications')

    department_users = CustomUser.objects.filter(department=department, role__in=['hr', 'department'])
    print(f"Users found: {department_users.count()}")
    print(f"User emails: {list(department_users.values_list('email', flat=True))}")

    if not department_users.exists():
        messages.error(request, f'Không tìm thấy người phỏng vấn nào trong phòng ban "{department}".')
        return redirect('hr:manage_applications')

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, interviewer_queryset=department_users)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = request.user
            interview.save()
            messages.success(request, 'Lịch phỏng vấn đã được tạo thành công.')
            return redirect('hr:manage_interviews')
    else:
        form = InterviewScheduleForm(interviewer_queryset=department_users, initial={'application': application})

    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'hr/schedule_interview.html', context)

# @login_required
# def manage_interviews(request):
#     if request.user.role not in ['hr', 'department']:
#         messages.error(request, 'Only HR and departments can manage interviews.')
#         return redirect('jobs:job_list')
#     if request.user.role == 'hr':
#         interviews = InterviewSchedule.objects.all()
#     else:
#         interviews = InterviewSchedule.objects.filter(created_by=request.user)
#     return render(request, 'hr/manage_interviews.html', {'interviews': interviews})

@login_required
def manage_interviews(request):
    user = request.user

    if user.role not in ['hr', 'department']:
        messages.error(request, 'Bạn không có quyền truy cập vào mục này.')
        return redirect('jobs:job_list')

    if user.role == 'hr':
        interviews = InterviewSchedule.objects.all()
    else:  # department
        interviews = InterviewSchedule.objects.filter(application__job__department=user.department)

    return render(request, 'hr/manage_interviews.html', {'interviews': interviews})

def company_info(request):
    company_info = CompanyInfo.objects.first()
    context = {'company_info': company_info}
    return render(request, 'hr/company_info.html', context)

def recruitment_analytics(request):
    status_counts = Application.objects.values('status').annotate(count=Count('id'))
    status_data = {
        'labels': [item['status'].capitalize() for item in status_counts],
        'counts': [item['count'] for item in status_counts]
    }
    department_counts = JobRequest.objects.values('department').annotate(count=Count('id'))
    department_data = {
        'labels': [item['department'] for item in department_counts],
        'counts': [item['count'] for item in department_counts]
    }
    context = {
        'status_data': status_data,
        'department_data': department_data,
    }
    return render(request, 'analytics/recruitment_analytics.html', context)

@login_required
def recruitment_requests_history(request):
    if request.user.role not in ['hr', 'director']:
        messages.error(request, 'Bạn không có quyền xem lịch sử yêu cầu tuyển dụng.')
        return redirect('jobs:job_list')
    
    job_requests = JobRequest.objects.all()
    
    department_filter = request.GET.get('department')
    if department_filter:
        job_requests = job_requests.filter(department=department_filter)
    
    job_requests = job_requests.order_by('-id')  # Hoặc theo ý bạn
    
    # Lấy danh sách phòng ban hiện có để hiển thị filter
    departments = JobRequest.objects.values_list('department', flat=True).distinct()
    
    context = {
        'job_requests': job_requests,
        'departments': departments,
        'selected_department': department_filter,
    }
    return render(request, 'hr/recruitment_requests_history.html', context)

@login_required
def update_application_status_inline(request, application_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ bộ phận nhân sự mới được cập nhật trạng thái đơn ứng tuyển.')
        return redirect('hr:manage_applications')

    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if application.status != 'pending':
            messages.error(request, 'Chỉ có thể thay đổi trạng thái khi đơn đang ở trạng thái chờ duyệt.')
            return redirect('hr:manage_applications')

        if status not in ['approved', 'pending', 'rejected']:
            messages.error(request, 'Trạng thái không hợp lệ.')
            return redirect('hr:manage_applications')

        if status == 'rejected':
            # Có thể lưu log trước khi xóa
            ActionLog.objects.create(
                user=request.user,
                action_type='reject_application',
                details=f'Đơn ứng tuyển {application.id} đã bị từ chối và xóa.',
                timestamp=timezone.now()
            )
            application.delete()
            messages.success(request, 'Đơn ứng tuyển đã bị từ chối và thông báo đến ứng viên.')
            return redirect('hr:manage_applications')

        if status == 'approved':
            application.status = 'approved'
            application.save()

            ActionLog.objects.create(
                user=request.user,
                action_type='approve_application',
                details=f'Đơn ứng tuyển {application.id} đã được duyệt.',
                timestamp=timezone.now()
            )
            messages.success(request, 'Đơn ứng tuyển đã được duyệt thành công.')
            return redirect('hr:manage_applications')

    # Nếu không phải POST request
    return redirect('hr:manage_applications')