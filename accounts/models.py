from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'hr')
        return self.create_user(email, password, **extra_fields)
DEPARTMENTS = [
    ('IT', 'Công nghệ thông tin'),
    ('HR', 'Nhân sự'),
    ('Finance', 'Tài chính'),
    ('Marketing', 'Marketing'),
]
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('hr', 'HR'),
        ('applicant', 'Applicant'),
        ('director', 'Director'),
        ('department', 'Department'),
    ]
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='applicant')
    # department = models.CharField(max_length=100, blank=True, help_text="Department or division within the company")
    department = models.CharField(max_length=100, choices=DEPARTMENTS, blank=True, default='', help_text="Phòng ban trong công ty")
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email