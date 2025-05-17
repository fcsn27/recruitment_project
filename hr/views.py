from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
def manage_applications(request):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can manage applications.')
        return redirect('jobs:job_list')
    applications = Application.objects.all()
    return render(request, 'hr/manage_applications.html', {'applications': applications})

@login_required
def update_application_status(request, application_id):
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can update application status.')
        return redirect('jobs:job_list')
    application = get_object_or_404(Application, id=application_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pending', 'approved', 'rejected']:
            application.status = status
            application.save()
            ActionLog.objects.create(
                user=request.user,
                action='update_application_status',
                job_request=None,
                details=f'Updated application {application.id} status to {status}',
                timestamp=timezone.now()
            )
            messages.success(request, f'Application status updated to {status}.')
        else:
            messages.error(request, 'Invalid status.')
        return redirect('hr:manage_applications')
    return render(request, 'hr/update_application_status.html', {'application': application})

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
    if request.user.role not in ['hr', 'department']:
        messages.error(request, 'Only HR and departments can view application status.')
        return redirect('jobs:job_list')
    applications = Application.objects.filter(job__created_by=request.user)
    return render(request, 'hr/application_status.html', {'applications': applications})

@login_required
def schedule_interview(request, application_id):
    if request.user.role not in ['hr', 'department']:
        messages.error(request, 'Only HR and departments can schedule interviews.')
        return redirect('jobs:job_list')
    application = get_object_or_404(Application, id=application_id)
    if application.job.created_by != request.user and request.user.role != 'hr':
        messages.error(request, 'You can only schedule interviews for your own job postings.')
        return redirect('hr:manage_applications')
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.created_by = request.user
            interview.save()
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('hr:manage_applications')
    else:
        form = InterviewScheduleForm(initial={'application': application})
    return render(request, 'hr/schedule_interview.html', {'form': form, 'application': application})

@login_required
def manage_interviews(request):
    if request.user.role not in ['hr', 'department']:
        messages.error(request, 'Only HR and departments can manage interviews.')
        return redirect('jobs:job_list')
    if request.user.role == 'hr':
        interviews = InterviewSchedule.objects.all()
    else:
        interviews = InterviewSchedule.objects.filter(created_by=request.user)
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