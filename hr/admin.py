from django.contrib import admin
from accounts.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'department', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('email', 'full_name')
    fields = ('email', 'full_name', 'role', 'department', 'phone_number', 'address', 'is_active', 'is_staff')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role != 'hr':
            return qs.none()
        return qs