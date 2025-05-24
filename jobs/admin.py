from django.contrib import admin
from .models import JobRequest, JobPosting, Application, ActionLog

@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'quantity', 'created_by')
    search_fields = ('title', 'department', 'created_by__email')
    list_filter = ('department',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'department')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'status', 'applied_at')
    list_filter = ('status',)

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'user', 'job_request', 'timestamp')
    list_filter = ('action_type',)
