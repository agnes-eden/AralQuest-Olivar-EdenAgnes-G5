from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'grade_level', 'school_name')
    list_filter = ('role', 'grade_level')
    search_fields = ('user__username', 'user__email', 'school_name')
