from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('analytics/', views.recruitment_analytics, name='recruitment_analytics'),
    path('company-info/manage/', views.manage_company_info, name='manage_company_info'),
    path('company-info/', views.company_info, name='company_info'),
    path('job-postings/', views.manage_job_postings, name='manage_job_postings'),
    path('job-postings/create/', views.create_job_posting, name='create_job_posting'),
    path('job-postings/edit/<int:job_id>/', views.edit_job_posting, name='edit_job_posting'),
    path('job-postings/delete/<int:job_id>/', views.delete_job_posting, name='delete_job_posting'),
    path('applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('history/', views.recruitment_history, name='recruitment_history'),
    path('application-status/', views.application_status, name='application_status'),
    path('applications/<int:application_id>/schedule-interview/', views.schedule_interview, name='schedule_interview'),
    path('interviews/', views.manage_interviews, name='manage_interviews'),
    path('requests/history/', views.recruitment_requests_history, name='recruitment_requests_history'),
    path('applications/<int:application_id>/update-status-inline/', views.update_application_status_inline, name='update_application_status_inline'),
]