from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import UserProfile


User = get_user_model()


class AccountFeatureTests(TestCase):
    def registration_data(self, **overrides):
        data = {
            'username': 'aralquest_student',
            'email': 'student@example.com',
            'first_name': 'Aral',
            'last_name': 'Student',
            'password1': 'Safe-Test-Password-519!',
            'password2': 'Safe-Test-Password-519!',
        }
        data.update(overrides)
        return data

    def create_user(self, username, email, role='STUDENT', password='Safe-Test-Password-519!'):
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role)
        return user

    def test_registration_creates_student_with_hashed_password(self):
        response = self.client.post(reverse('register'), self.registration_data())

        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='aralquest_student')
        self.assertTrue(user.check_password('Safe-Test-Password-519!'))
        self.assertFalse(user.password == 'Safe-Test-Password-519!')
        self.assertEqual(user.profile.role, 'STUDENT')

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        self.create_user('existing', 'student@example.com')

        response = self.client.post(
            reverse('register'),
            self.registration_data(email='STUDENT@example.com'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with that email already exists.')
        self.assertEqual(User.objects.count(), 1)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('register'),
            self.registration_data(password2='Different-Password-519!'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_login_redirects_by_role_and_logout_ends_session(self):
        user = self.create_user('teacher', 'teacher@example.com', role='TEACHER')

        response = self.client.post(reverse('login'), {
            'username': user.username,
            'password': 'Safe-Test-Password-519!',
        })

        self.assertRedirects(
            response,
            reverse('dashboard_redirect'),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.get(reverse('dashboard_redirect')),
            reverse('teacher_dashboard'),
            fetch_redirect_response=False,
        )
        self.assertEqual(self.client.get(reverse('teacher_dashboard')).status_code, 200)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertRedirects(
            self.client.get(reverse('teacher_dashboard')),
            f'{reverse("login")}?next={reverse("teacher_dashboard")}',
            fetch_redirect_response=False,
        )

    def test_user_cannot_open_another_role_dashboard(self):
        user = self.create_user('student', 'student@example.com')
        self.client.force_login(user)

        response = self.client.get(reverse('teacher_dashboard'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/student_dashboard.html')

    def test_invalid_login_shows_an_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'nobody',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_profile_updates_only_the_logged_in_users_data(self):
        user = self.create_user('student', 'student@example.com')
        other_user = self.create_user('other', 'other@example.com')
        self.client.force_login(user)

        response = self.client.post(reverse('profile'), {
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'student@example.com',
            'grade_level': '4',
            'school_name': 'AralQuest School',
        })

        self.assertRedirects(response, reverse('profile'))
        user.refresh_from_db()
        other_user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.profile.grade_level, 4)
        self.assertEqual(other_user.first_name, '')
