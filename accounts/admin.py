from django.contrib import admin

from .models import LearningQuest, QuestAttempt, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'grade_level', 'school_name')
    list_filter = ('role', 'grade_level')
    search_fields = ('user__username', 'user__email', 'school_name')


@admin.register(LearningQuest)
class LearningQuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade_level', 'creator', 'is_published')
    list_filter = ('subject', 'grade_level', 'is_published')
    search_fields = ('title', 'creator__username')


@admin.register(QuestAttempt)
class QuestAttemptAdmin(admin.ModelAdmin):
    list_display = ('quest', 'learner', 'is_correct', 'updated_at')
    list_filter = ('is_correct',)
    search_fields = ('quest__title', 'learner__username')
