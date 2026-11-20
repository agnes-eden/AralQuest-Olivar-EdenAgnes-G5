from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('teacher/quests/', views.teacher_quests, name='teacher_quests'),
    path('teacher/quests/create/', views.quest_create, name='quest_create'),
    path('teacher/quests/<int:quest_id>/edit/', views.quest_edit, name='quest_edit'),
    path('teacher/quests/<int:quest_id>/delete/', views.quest_delete, name='quest_delete'),
    path('teacher/quests/<int:quest_id>/results/', views.quest_results, name='quest_results'),
    path('quests/', views.student_quests, name='student_quests'),
    path('quests/<int:quest_id>/', views.quest_play, name='quest_play'),
    path('progress/', views.student_progress, name='student_progress'),
]
