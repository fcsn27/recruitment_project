from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.recruitment_analytics, name='recruitment_analytics'),
]