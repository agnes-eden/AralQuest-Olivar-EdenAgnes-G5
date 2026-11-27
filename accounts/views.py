from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from .forms import (
    LearningQuestForm,
    QuestAnswerForm,
    RegistrationForm,
    UserDetailsForm,
    UserProfileForm,
)
from .models import LearningQuest, QuestAttempt, UserProfile


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            UserProfile.objects.create(user=user, role='STUDENT')
        messages.success(request, 'Your account was created. You can now log in.')
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_redirect(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


def role_required(role):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            if profile.role != role:
                messages.error(request, 'You do not have permission to view that dashboard.')
                return redirect('dashboard_redirect')
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


@role_required('STUDENT')
def student_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/student_dashboard.html', {
        'profile': profile,
        'quest_count': LearningQuest.objects.filter(
            is_published=True,
            **({'grade_level': profile.grade_level} if profile.grade_level else {}),
        ).count(),
        'completed_count': QuestAttempt.objects.filter(learner=request.user).count(),
    })


@role_required('TEACHER')
def teacher_dashboard(request):
    student_count = UserProfile.objects.filter(role='STUDENT').count()
    return render(request, 'accounts/teacher_dashboard.html', {
        'student_count': student_count,
        'quest_count': LearningQuest.objects.filter(creator=request.user).count(),
    })


@role_required('TEACHER')
def teacher_activity(request):
    students = QuestAttempt.objects.filter(
        quest__creator=request.user,
        learner__profile__role='STUDENT',
    ).values(
        'learner_id',
        username=F('learner__username'),
        first_name=F('learner__first_name'),
        last_name=F('learner__last_name'),
    ).annotate(
        quests_attempted=Count('quest_id', distinct=True),
        attempt_count=Count('pk'),
        correct_count=Count('pk', filter=Q(is_correct=True)),
        last_activity=Max('created_at'),
    ).order_by('-last_activity', 'last_name', 'first_name', 'username')
    return render(request, 'accounts/teacher_activity.html', {
        'students': students,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserDetailsForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile,
        )
        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()
        if user_form_valid and profile_form_valid:
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserDetailsForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': user_profile,
    })


@role_required('TEACHER')
def teacher_quests(request):
    quests = LearningQuest.objects.filter(creator=request.user).annotate(
        attempt_count=Count('attempts'),
    )
    return render(request, 'accounts/teacher_quests.html', {'quests': quests})


@role_required('TEACHER')
@require_http_methods(['GET', 'POST'])
def quest_create(request):
    form = LearningQuestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        quest = form.save(commit=False)
        quest.creator = request.user
        quest.save()
        messages.success(request, 'Your learning quest has been created.')
        return redirect('teacher_quests')
    return render(request, 'accounts/quest_form.html', {
        'form': form,
        'page_title': 'Create a learning quest',
    })


@role_required('TEACHER')
@require_http_methods(['GET', 'POST'])
def quest_edit(request, quest_id):
    quest = get_object_or_404(LearningQuest, pk=quest_id, creator=request.user)
    form = LearningQuestForm(request.POST or None, instance=quest)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your learning quest has been updated.')
        return redirect('teacher_quests')
    return render(request, 'accounts/quest_form.html', {
        'form': form,
        'page_title': 'Edit learning quest',
        'quest': quest,
    })


@role_required('TEACHER')
@require_http_methods(['GET', 'POST'])
def quest_delete(request, quest_id):
    quest = get_object_or_404(LearningQuest, pk=quest_id, creator=request.user)
    if request.method == 'POST':
        quest.delete()
        messages.success(request, 'The learning quest has been deleted.')
        return redirect('teacher_quests')
    return render(request, 'accounts/quest_delete.html', {'quest': quest})


@role_required('TEACHER')
def quest_results(request, quest_id):
    quest = get_object_or_404(LearningQuest, pk=quest_id, creator=request.user)
    attempts = quest.attempts.select_related('learner').all()
    return render(request, 'accounts/quest_results.html', {
        'quest': quest,
        'attempts': attempts,
    })


@role_required('STUDENT')
def student_quests(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    quests = LearningQuest.objects.filter(is_published=True)
    if profile.grade_level:
        quests = quests.filter(grade_level=profile.grade_level)
    quests = list(quests)
    attempts = {
        attempt.quest_id: attempt
        for attempt in QuestAttempt.objects.filter(
            learner=request.user,
            quest__in=quests,
        )
    }
    for quest in quests:
        quest.user_attempt = attempts.get(quest.pk)
    return render(request, 'accounts/student_quests.html', {
        'quests': quests,
        'grade_level': profile.grade_level,
    })


@role_required('STUDENT')
@require_http_methods(['GET', 'POST'])
def quest_play(request, quest_id):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    quests = LearningQuest.objects.filter(pk=quest_id, is_published=True)
    if profile.grade_level:
        quests = quests.filter(grade_level=profile.grade_level)
    quest = get_object_or_404(quests)
    previous_attempt = QuestAttempt.objects.filter(
        learner=request.user,
        quest=quest,
    ).first()

    if request.method == 'POST':
        form = QuestAnswerForm(request.POST, quest=quest)
        if form.is_valid():
            selected_answer = form.cleaned_data['answer']
            attempt, _ = QuestAttempt.objects.update_or_create(
                learner=request.user,
                quest=quest,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer == quest.correct_answer,
                },
            )
            if attempt.is_correct:
                messages.success(request, 'Correct! You completed this quest.')
            else:
                messages.info(request, 'Good try! Review the question and give it another go.')
            return redirect('quest_play', quest_id=quest.pk)
    else:
        form = QuestAnswerForm(
            quest=quest,
            initial={'answer': previous_attempt.selected_answer} if previous_attempt else None,
        )

    return render(request, 'accounts/quest_play.html', {
        'quest': quest,
        'form': form,
        'attempt': previous_attempt,
    })


@role_required('STUDENT')
def student_progress(request):
    attempts = QuestAttempt.objects.filter(
        learner=request.user,
        quest__is_published=True,
    ).select_related('quest')
    return render(request, 'accounts/student_progress.html', {'attempts': attempts})
