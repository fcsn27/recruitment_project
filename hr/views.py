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
from django.db.models import Q

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
def manage_applications(request):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ bộ phận nhân sự mới được phép quản lý đơn ứng tuyển.')
        return redirect('jobs:job_list')
    
    applications = Application.objects.all()
    return render(request, 'hr/manage_applications.html', {'applications': applications})

@login_required
def update_application_status(request, application_id):
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ nhân sự mới được cập nhật trạng thái.')
        return redirect('hr:manage_applications')

    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', 'Không phù hợp với tiêu chí ứng tuyển')

        if status not in ['pending', 'passed', 'rejected']:
            messages.error(request, 'Trạng thái không hợp lệ.')
            return redirect('hr:manage_applications')

        application.status = status
        if status == 'rejected':
            application.rejection_reason = rejection_reason
        else:
            application.rejection_reason = None

        application.save()

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

@login_required
def application_status(request):
    user = request.user
    if user.role == 'applicant':
        applications = Application.objects.filter(user=user)
    elif user.role in ['department', 'hr']:
        applications = Application.objects.all()
    else:
        applications = Application.objects.none()
        messages.error(request, 'Bạn không có quyền xem trạng thái đơn ứng tuyển.')
    
    return render(request, 'hr/application_status.html', {'applications': applications})

@login_required
def schedule_interview(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Chỉ HR được phép lên lịch phỏng vấn
    if request.user.role != 'hr':
        messages.error(request, 'Chỉ HR có quyền lên lịch phỏng vấn.')
        return redirect('hr:application_status')
    
    # Kiểm tra trạng thái ứng viên
    if application.status != 'approved':
        messages.error(request, 'Chỉ có thể lên lịch phỏng vấn cho ứng viên đã được duyệt.')
        return redirect('hr:manage_interviews')
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = request.user
            interview.department = application.job.department  # Gán phòng ban phỏng vấn
            interview.save()
            application.status = 'scheduled'
            application.save()
            ActionLog.objects.create(
                user=request.user,
                action_type='schedule_interview',
                job_request=application.job.created_by.jobrequest_set.first() if application.job.created_by.jobrequest_set.exists() else None,
                details=f'Lên lịch phỏng vấn cho đơn {application.id} vào {interview.scheduled_time} với phòng ban {interview.department}',
                timestamp=timezone.now()
            )
            messages.success(request, 'Lên lịch phỏng vấn thành công.')
            return redirect('hr:manage_interviews')
    else:
        form = InterviewScheduleForm()
    
    return render(request, 'hr/schedule_interview.html', {
        'form': form,
        'application': application,
    })

@login_required
def manage_interviews(request):
    if request.user.role == 'hr':
        # HR thấy tất cả ứng viên đã duyệt và lịch phỏng vấn
        approved_applications = Application.objects.filter(status='approved')
        interviews = InterviewSchedule.objects.all()
    elif request.user.role == 'applicant':
        # Ứng viên chỉ thấy lịch phỏng vấn của họ
        approved_applications = Application.objects.none()  # Không thấy ứng viên khác
        interviews = InterviewSchedule.objects.filter(application__user=request.user)
    elif request.user.department:
        # Phòng ban thấy ứng viên và lịch phỏng vấn của phòng ban họ
        approved_applications = Application.objects.filter(
            status='approved',
            job__department=request.user.department
        )
        interviews = InterviewSchedule.objects.filter(
            department=request.user.department
        )
    else:
        # Người dùng không có quyền
        messages.error(request, 'Bạn không có quyền truy cập vào mục này.')
        return redirect('jobs:job_list')
    
    return render(request, 'hr/manage_interviews.html', {
        'approved_applications': approved_applications,
        'interviews': interviews,
        'user_role': request.user.role,
        'user_department': request.user.department
    })

def company_info(request):
    company_info = CompanyInfo.objects.first()
    context = {'company_info': company_info}
    return render(request, 'hr/company_info.html', context)

@login_required
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
        messages.error(request, 'Chỉ nhân sự mới được cập nhật trạng thái đơn ứng tuyển.')
        return redirect('hr:manage_applications')

    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', 'Không phù hợp với tiêu chí ứng tuyển')

        # Cho phép cập nhật từ trạng thái 'pending' hoặc 'scheduled'
        if application.status not in ['pending', 'scheduled']:
            messages.error(request, 'Chỉ có thể thay đổi trạng thái khi đơn đang ở trạng thái chờ duyệt hoặc đã lên lịch phỏng vấn.')
            return redirect('hr:manage_applications')

        # Kiểm tra trạng thái hợp lệ
        if status not in ['pending', 'approved', 'scheduled', 'passed', 'rejected']:
            messages.error(request, 'Trạng thái không hợp lệ.')
            return redirect('hr:manage_applications')

        if status == 'rejected':
            ActionLog.objects.create(
                user=request.user,
                action_type='reject_application',
                details=f'Đơn ứng tuyển {application.id} đã bị từ chối và xóa. Lý do: {rejection_reason}',
                timestamp=timezone.now()
            )
            application.delete()
            messages.success(request, 'Đơn ứng tuyển đã bị từ chối và thông báo đến ứng viên.')
            return redirect('hr:manage_applications')

        if status == 'passed':
            application.status = 'passed'
            application.rejection_reason = None
            application.save()

            ActionLog.objects.create(
                user=request.user,
                action_type='approve_application',
                details=f'Đơn ứng tuyển {application.id} đã đạt tuyển.',
                timestamp=timezone.now()
            )
            messages.success(request, 'Đơn ứng tuyển đã đạt tuyển thành công.')
            return redirect('hr:manage_applications')

        if status == 'approved':
            application.status = 'approved'
            application.rejection_reason = None
            application.save()

            ActionLog.objects.create(
                user=request.user,
                action_type='approve_application',
                details=f'Đơn ứng tuyển {application.id} đã được duyệt để phỏng vấn.',
                timestamp=timezone.now()
            )
            messages.success(request, 'Đơn ứng tuyển đã được duyệt để phỏng vấn.')
            return redirect('hr:manage_applications')

        if status == 'scheduled':
            # Nếu trạng thái là 'scheduled', cần kiểm tra xem đã có lịch phỏng vấn chưa
            if not InterviewSchedule.objects.filter(application=application).exists():
                messages.error(request, 'Không thể đặt trạng thái "Đã lên lịch phỏng vấn" khi chưa có lịch phỏng vấn.')
                return redirect('hr:manage_applications')
            application.status = 'scheduled'
            application.save()

            ActionLog.objects.create(
                user=request.user,
                action_type='update_application_status',
                details=f'Đơn ứng tuyển {application.id} đã được cập nhật sang trạng thái đã lên lịch phỏng vấn.',
                timestamp=timezone.now()
            )
            messages.success(request, 'Đơn ứng tuyển đã được cập nhật thành công.')
            return redirect('hr:manage_applications')

    return redirect('hr:manage_applications')