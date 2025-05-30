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

# class Application(models.Model):
#     job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     cv = models.FileField(upload_to='cvs/')
#     status = models.CharField(max_length=20, choices=[
#         ('pending', 'Pending'),
#         ('accepted', 'Accepted'),
#         ('rejected', 'Rejected'),
#     ], default='pending')
#     applied_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.email} - {self.job.title}"
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
    
    rejection_reason = models.TextField(blank=True, null=True)  # Thêm trường này
    
    def __str__(self):
        return f"{self.user.email} - {self.job.title}"


class JobRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField()
    reason = models.TextField(blank=True, null=True)  # Lý do tuyển dụng (có thể để trống)
    rejection_reason = models.TextField(blank=True, null=True)  # Lý do từ chối (nếu có)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

class ActionLog(models.Model):
    action_type = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='action_logs', null=True, blank=True)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)