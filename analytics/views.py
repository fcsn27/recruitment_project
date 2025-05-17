from django.shortcuts import render
from jobs.models import Application, JobRequest
from django.db.models import Count

def recruitment_analytics(request):
    # Đếm số ứng tuyển theo trạng thái
    status_counts = Application.objects.values('status').annotate(count=Count('id'))
    status_data = {
        'labels': [item['status'] for item in status_counts],
        'counts': [item['count'] for item in status_counts]
    }

    # Đếm số vị trí theo phòng ban
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