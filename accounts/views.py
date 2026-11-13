from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from .forms import RegistrationForm, UserDetailsForm, UserProfileForm
from .models import UserProfile


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
    return render(request, 'accounts/student_dashboard.html', {'profile': profile})


@role_required('TEACHER')
def teacher_dashboard(request):
    student_count = UserProfile.objects.filter(role='STUDENT').count()
    return render(request, 'accounts/teacher_dashboard.html', {'student_count': student_count})


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
