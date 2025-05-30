from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobPosting, Application, JobRequest, ActionLog
from .forms import ApplicationForm, JobRequestForm, JobPostingForm
from accounts.models import CustomUser
from django.utils import timezone

def job_list(request):
    jobs = JobPosting.objects.filter(is_active=True)
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.user.role != 'applicant':
        messages.error(request, 'Only applicants can apply for jobs.')
        return redirect('jobs:job_list')
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('jobs:job_list')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

# @login_required
# def application_status(request):
#     if request.user.role != 'applicant':
#         messages.error(request, 'Only applicants can view application status.')
#         return redirect('jobs:job_list')
#     applications = Application.objects.filter(user=request.user)
#     return render(request, 'hr/application_status.html', {'applications': applications})
@login_required
def application_status(request):
    if request.user.role == 'applicant':
        applications = Application.objects.filter(user=request.user)

    elif request.user.role == 'department':
        # Chỉ xem đơn thuộc phòng ban của họ và đã được HR duyệt (approved trở lên)
        applications = Application.objects.filter(
            job__department=request.user.role,
            status__in=['approved', 'passed', 'rejected']  # hoặc status != 'pending'
        )

    elif request.user.role == 'hr':
        applications = Application.objects.all()

    else:
        messages.error(request, 'Bạn không có quyền truy cập vào mục này.')
        return redirect('jobs:job_list')
    
    return render(request, 'hr/application_status.html', {'applications': applications})

@login_required
def create_job_request(request):
    if request.user.role != 'department':
        messages.error(request, 'Bạn không có quyền tạo yêu cầu tuyển dụng.')
        return redirect('jobs:job_list')
    
    if request.method == 'POST':
        form = JobRequestForm(request.POST)
        if form.is_valid():
            job_request = form.save(commit=False)
            # Gán department dựa trên user.role
            job_request.department = request.user.role  # hoặc nếu role khác tên với department thì map lại
            job_request.created_by = request.user
            job_request.status = 'pending'
            job_request.save()
            messages.success(request, 'Tạo yêu cầu tuyển dụng thành công.')
            return redirect('jobs:manage_job_requests')
    else:
        form = JobRequestForm()
    
    return render(request, 'jobs/create_job_request.html', {'form': form})

@login_required
def manage_job_requests(request):
    if request.user.role == 'director':
        job_requests = JobRequest.objects.all()
    else:
        job_requests = JobRequest.objects.filter(created_by=request.user)
    return render(request, 'jobs/manage_job_requests.html', {'job_requests': job_requests})

@login_required
def job_request_detail(request, request_id):
    if request.user.role not in ['director', 'hr', 'department']:
        messages.error(request, 'You do not have permission to view job request details.')
        return redirect('jobs:job_list')
    job_request = get_object_or_404(JobRequest, id=request_id)
    if request.user.role == 'department' and job_request.created_by != request.user:
        messages.error(request, 'You can only view your own job requests.')
        return redirect('jobs:manage_job_requests')
    if request.user.role == 'hr' and job_request.created_by != request.user and job_request.status == 'pending':
        messages.error(request, 'HR can only view their own job requests or approved/rejected requests.')
        return redirect('jobs:manage_job_requests')
    return render(request, 'jobs/job_request_detail.html', {'job_request': job_request})

@login_required
def edit_job_request(request, request_id):
    if request.user.role != 'director':
        messages.error(request, 'Only directors can edit job requests.')
        return redirect('jobs:job_list')
    job_request = get_object_or_404(JobRequest, id=request_id)
    if job_request.status != 'pending':
        messages.error(request, 'Only pending job requests can be edited.')
        return redirect('jobs:manage_job_requests')
    if request.method == 'POST':
        form = JobRequestForm(request.POST, instance=job_request)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job request "{job_request.title}" updated successfully.')
            return redirect('jobs:manage_job_requests')
    else:
        form = JobRequestForm(instance=job_request)
    return render(request, 'jobs/edit_job_request.html', {'form': form, 'job_request': job_request})

@login_required
def approve_job_request(request, request_id):
    if request.user.role != 'director':
        messages.error(request, 'Chỉ giám đốc mới có quyền duyệt yêu cầu.')
        return redirect('jobs:job_list')
    
    job_request = get_object_or_404(JobRequest, id=request_id)
    
    if job_request.status != 'pending':
        messages.error(request, 'Chỉ duyệt được các yêu cầu đang chờ xử lý.')
        return redirect('jobs:manage_job_requests')

    # Duyệt ngay, không cần nhập lý do
    job_request.status = 'approved'
    job_request.save()

    # Tạo bài đăng tuyển dụng tương ứng
    JobPosting.objects.create(
        title=job_request.title,
        department=job_request.department,
        description=job_request.reason or '',  # hoặc dùng description nếu phù hợp
        is_active=True,
        created_by=request.user,
    )

    messages.success(request, f'Yêu cầu "{job_request.title}" đã được duyệt và đăng bài tuyển dụng.')
    return redirect('jobs:manage_job_requests')

@login_required
def reject_job_request(request, request_id):
    if request.user.role != 'director':
        messages.error(request, 'Only directors can reject job requests.')
        return redirect('jobs:job_list')

    job_request = get_object_or_404(JobRequest, id=request_id)

    if job_request.status != 'pending':
        messages.error(request, 'Only pending job requests can be rejected.')
        return redirect('jobs:manage_job_requests')

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        if not rejection_reason:
            messages.error(request, 'Rejection reason is required.')
            return render(request, 'jobs/reject_job_request.html', {'job_request': job_request})

        job_request.status = 'rejected'
        job_request.rejection_reason = rejection_reason
        job_request.save()

        ActionLog.objects.create(
            user=request.user,
            action_type='reject',
            job_request=job_request,
            details=f'Rejected with reason: {rejection_reason}',
            timestamp=timezone.now()
        )

        messages.success(request, f'Job request "{job_request.title}" rejected successfully.')
        return redirect('jobs:manage_job_requests')

    return render(request, 'jobs/reject_job_request.html', {'job_request': job_request})

@login_required
def delete_job_request(request, request_id):
    job_request = get_object_or_404(JobRequest, id=request_id)

    # Chỉ cho phép người tạo hoặc director xoá
    if request.user.role != 'director' and job_request.created_by != request.user:
        messages.error(request, 'Bạn không có quyền xoá yêu cầu này.')
        return redirect('jobs:manage_job_requests')

    # Chỉ cho phép xoá khi trạng thái là pending (hoặc bạn có thể cho xoá luôn)
    if job_request.status != 'pending':
        messages.error(request, 'Chỉ có thể xoá yêu cầu đang chờ duyệt.')
        return redirect('jobs:manage_job_requests')

    if request.method == 'POST':
        job_request.delete()
        messages.success(request, 'Xoá yêu cầu tuyển dụng thành công.')
        return redirect('jobs:manage_job_requests')

    # Nếu muốn xác nhận trước khi xoá, bạn có thể render 1 trang xác nhận
    return render(request, 'jobs/confirm_delete_job_request.html', {'job_request': job_request})

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        application.status = new_status
        application.save()

        # Nếu không có job_request liên quan, bạn có thể bỏ qua hoặc dùng application.job nếu cần
        ActionLog.objects.create(
            user=request.user,
            job_request=application.job.created_by.jobrequest_set.first(),  # hoặc cách bạn xác định đúng job_request
            action_type='updated status',
            details=f'Cập nhật đơn ứng tuyển {application.id} sang trạng thái "{new_status}"'
        )

        messages.success(request, 'Trạng thái đơn ứng tuyển đã được cập nhật.')
        return redirect('some_view')  # đổi thành tên view phù hợp

    return redirect('some_view')