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
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('jobs:job_list')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
def application_status(request):
    if request.user.role != 'applicant':
        messages.error(request, 'Only applicants can view application status.')
        return redirect('jobs:job_list')
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'jobs/application_status.html', {'applications': applications})

# @login_required
# def create_job_request(request):
#     if request.user.role not in ['department', 'hr']:
#         messages.error(request, 'You do not have permission to create a job request.')
#         return redirect('jobs:job_list')
#     if request.method == 'POST':
#         form = JobRequestForm(request.POST)
#         if form.is_valid():
#             job_request = form.save(commit=False)
#             job_request.created_by = request.user
#             job_request.save()
#             messages.success(request, 'Job request created successfully.')
#             return redirect('jobs:manage_job_requests')
#     else:
#         form = JobRequestForm()
#     return render(request, 'jobs/create_job_request.html', {'form': form})
def create_job_request(request):
    if request.method == 'POST':
        form = JobRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobRequestForm()
    return render(request, 'jobs/create_job_request.html', {'form': form})

@login_required
def manage_job_requests(request):
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
        messages.error(request, 'Only directors can approve job requests.')
        return redirect('jobs:job_list')
    job_request = get_object_or_404(JobRequest, id=request_id)
    if job_request.status != 'pending':
        messages.error(request, 'Only pending job requests can be approved.')
        return redirect('jobs:manage_job_requests')
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.created_by = request.user
            job_posting.save()
            job_request.status = 'approved'
            job_request.save()
            messages.success(request, f'Job request "{job_request.title}" approved for {job_request.created_by.email}.', extra_tags=f'user_{job_request.created_by.id}')
            hr_users = CustomUser.objects.filter(role='hr')
            for hr_user in hr_users:
                messages.info(request, f'New job posting "{job_posting.title}" created from request "{job_request.title}".', extra_tags=f'user_{hr_user.id}')
            messages.success(request, f'Job request "{job_request.title}" approved and job posting created.')
            return redirect('jobs:manage_job_requests')
    else:
        form = JobPostingForm(initial={
            'title': job_request.title,
            'department': job_request.department,
            'description': job_request.description,
            'is_active': True
        })
    return render(request, 'jobs/approve_job_request.html', {'form': form, 'job_request': job_request})

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
        rejection_reason = request.POST.get('rejection_reason')
        if not rejection_reason:
            messages.error(request, 'Rejection reason is required.')
            return render(request, 'jobs/reject_job_request.html', {'job_request': job_request})
        job_request.status = 'rejected'
        job_request.rejection_reason = rejection_reason
        job_request.save()
        ActionLog.objects.create(
            user=request.user,
            action='reject',
            job_request=job_request,
            details=f'Rejected with reason: {rejection_reason}',
            timestamp=timezone.now()
        )
        messages.success(request, f'Job request "{job_request.title}" rejected for {job_request.created_by.email}.', extra_tags=f'user_{job_request.created_by.id}')
        messages.success(request, f'Job request "{job_request.title}" rejected with reason: {rejection_reason}.')
        return redirect('jobs:manage_job_requests')
    return render(request, 'jobs/reject_job_request.html', {'job_request': job_request})