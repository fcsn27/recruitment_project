from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from jobs.views import job_list

urlpatterns = [
    path('', job_list, name='home'),  # Trang chủ
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # path('jobs/', include('jobs.urls')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('hr/', include('hr.urls')),
    path('analytics/', include('analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)