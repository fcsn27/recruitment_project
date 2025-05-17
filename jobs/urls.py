from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('application_status/', views.application_status, name='application_status'),
    path('request/', views.create_job_request, name='create_job_request'),
    path('job_requests/', views.manage_job_requests, name='manage_job_requests'),
    path('job_requests/detail/<int:request_id>/', views.job_request_detail, name='job_request_detail'),
    path('job_requests/edit/<int:request_id>/', views.edit_job_request, name='edit_job_request'),
    path('job_requests/approve/<int:request_id>/', views.approve_job_request, name='approve_job_request'),
    path('job_requests/reject/<int:request_id>/', views.reject_job_request, name='reject_job_request'),
]