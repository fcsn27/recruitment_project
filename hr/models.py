from django.db import models
from accounts.models import CustomUser
from jobs.models import Application

class CompanyInfo(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=200)
    website = models.URLField(max_length=200)
    email = models.EmailField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Thông tin doanh nghiệp"
        verbose_name_plural = "Thông tin doanh nghiệp"

class InterviewSchedule(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    interviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='interviews')
    scheduled_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_interviews')

    def __str__(self):
        return f"Interview for {self.application.job.title} at {self.scheduled_time}"

class ActionLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hr_action_logs')
    action = models.CharField(max_length=100)
    details = models.TextField()
    job_request = models.ForeignKey('jobs.JobRequest', null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)