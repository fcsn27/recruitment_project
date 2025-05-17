from django.db import models
from accounts.models import CustomUser

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='cvs/')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.job.title}"

class JobRequest(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField()
    reason = models.TextField(blank=True, null=True)  # Cho phép null
    rejection_reason = models.TextField(blank=True, null=True)
    actionlog = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class ActionLog(models.Model):
    action_type = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='action_logs')
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} by {self.user.email} at {self.timestamp}"