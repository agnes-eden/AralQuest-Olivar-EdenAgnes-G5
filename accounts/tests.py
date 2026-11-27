from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import LearningQuest, QuestAttempt, UserProfile


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


class LearningQuestTests(TestCase):
    def create_user(self, username, role):
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='Safe-Test-Password-519!',
        )
        UserProfile.objects.create(user=user, role=role, grade_level=3)
        return user

    def create_quest(self, creator, **overrides):
        data = {
            'title': 'The Number Trail',
            'subject': 'MATH',
            'grade_level': 3,
            'question': 'What is 2 + 3?',
            'choice_a': '4',
            'choice_b': '5',
            'choice_c': '6',
            'choice_d': '7',
            'correct_answer': 'B',
        }
        data.update(overrides)
        return LearningQuest.objects.create(creator=creator, **data)

    def test_teacher_can_create_edit_view_results_and_delete_own_quest(self):
        teacher = self.create_user('teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        self.client.force_login(teacher)

        response = self.client.post(reverse('quest_create'), {
            'title': 'The Number Trail',
            'subject': 'MATH',
            'grade_level': 3,
            'question': 'What is 2 + 3?',
            'choice_a': '4',
            'choice_b': '5',
            'choice_c': '6',
            'choice_d': '7',
            'correct_answer': 'B',
            'is_published': 'on',
        })
        self.assertRedirects(response, reverse('teacher_quests'))
        quest = LearningQuest.objects.get(title='The Number Trail')
        self.assertEqual(quest.creator, teacher)

        QuestAttempt.objects.create(
            learner=learner,
            quest=quest,
            selected_answer='B',
            is_correct=True,
        )
        self.assertContains(
            self.client.get(reverse('quest_results', args=[quest.pk])),
            learner.username,
        )

        response = self.client.post(reverse('quest_edit', args=[quest.pk]), {
            'title': 'Addition Trail',
            'subject': 'MATH',
            'grade_level': 3,
            'question': 'What is 2 + 3?',
            'choice_a': '4',
            'choice_b': '5',
            'choice_c': '6',
            'choice_d': '7',
            'correct_answer': 'B',
            'is_published': 'on',
        })
        self.assertRedirects(response, reverse('teacher_quests'))
        quest.refresh_from_db()
        self.assertEqual(quest.title, 'Addition Trail')

        response = self.client.post(reverse('quest_delete', args=[quest.pk]))
        self.assertRedirects(response, reverse('teacher_quests'))
        self.assertFalse(LearningQuest.objects.filter(pk=quest.pk).exists())

    def test_teacher_activity_summarizes_students_on_only_their_quests(self):
        teacher = self.create_user('teacher', 'TEACHER')
        other_teacher = self.create_user('other_teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        other_learner = self.create_user('other_learner', 'STUDENT')
        first_quest = self.create_quest(teacher)
        second_quest = self.create_quest(
            teacher,
            title='A Reading Quest',
            subject='READING',
        )
        other_quest = self.create_quest(other_teacher, title='Another Teacher Quest')

        QuestAttempt.objects.create(
            learner=learner,
            quest=first_quest,
            selected_answer='B',
            is_correct=True,
        )
        QuestAttempt.objects.create(
            learner=learner,
            quest=second_quest,
            selected_answer='A',
            is_correct=False,
        )
        QuestAttempt.objects.create(
            learner=other_learner,
            quest=other_quest,
            selected_answer='B',
            is_correct=True,
        )
        self.client.force_login(teacher)

        response = self.client.get(reverse('teacher_activity'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, learner.username)
        self.assertNotContains(response, other_learner.username)
        activity = response.context['students'].get()
        self.assertEqual(activity['quests_attempted'], 2)
        self.assertEqual(activity['attempt_count'], 2)
        self.assertEqual(activity['correct_count'], 1)

    def test_student_cannot_view_teacher_activity(self):
        learner = self.create_user('learner', 'STUDENT')
        self.client.force_login(learner)

        response = self.client.get(reverse('teacher_activity'))

        self.assertEqual(response.status_code, 302)

    def test_student_answer_history_keeps_each_attempt(self):
        teacher = self.create_user('teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        quest = self.create_quest(teacher)
        self.client.force_login(learner)

        response = self.client.post(reverse('quest_play', args=[quest.pk]), {'answer': 'A'})
        self.assertRedirects(response, reverse('quest_play', args=[quest.pk]))
        first_attempt = QuestAttempt.objects.get(learner=learner, quest=quest)
        self.assertFalse(first_attempt.is_correct)

        self.client.post(reverse('quest_play', args=[quest.pk]), {'answer': 'B'})
        attempts = QuestAttempt.objects.filter(
            learner=learner,
            quest=quest,
        ).order_by('created_at', 'pk')
        self.assertEqual(attempts.count(), 2)
        self.assertEqual(
            list(attempts.values_list('selected_answer', flat=True)),
            ['A', 'B'],
        )
        self.assertEqual(
            list(attempts.values_list('is_correct', flat=True)),
            [False, True],
        )
        progress_response = self.client.get(reverse('student_progress'))
        self.assertContains(progress_response, 'Attempt 1')
        self.assertContains(progress_response, 'Attempt 2')

    def test_roles_and_ownership_are_enforced(self):
        teacher = self.create_user('teacher', 'TEACHER')
        other_teacher = self.create_user('other_teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        quest = self.create_quest(teacher)

        self.client.force_login(learner)
        self.assertEqual(self.client.get(reverse('teacher_quests')).status_code, 302)
        self.assertEqual(self.client.get(reverse('quest_play', args=[quest.pk])).status_code, 200)

        self.client.force_login(other_teacher)
        self.assertEqual(self.client.get(reverse('quest_edit', args=[quest.pk])).status_code, 404)
        response = self.client.post(reverse('quest_delete', args=[quest.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(LearningQuest.objects.filter(pk=quest.pk).exists())

    def test_invalid_answer_is_not_saved(self):
        teacher = self.create_user('teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        quest = self.create_quest(teacher)
        self.client.force_login(learner)

        response = self.client.post(reverse('quest_play', args=[quest.pk]), {'answer': 'Z'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a valid choice')
        self.assertFalse(QuestAttempt.objects.exists())

    def test_teacher_cannot_create_quest_with_duplicate_answer_choices(self):
        teacher = self.create_user('teacher', 'TEACHER')
        self.client.force_login(teacher)

        response = self.client.post(reverse('quest_create'), {
            'title': 'The Number Trail',
            'subject': 'MATH',
            'grade_level': 3,
            'question': 'What is 2 + 3?',
            'choice_a': '5',
            'choice_b': '5',
            'choice_c': '6',
            'choice_d': '7',
            'correct_answer': 'A',
            'is_published': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Each answer choice must be different.')
        self.assertFalse(LearningQuest.objects.exists())

    def test_student_sees_only_matching_published_quests_and_own_progress(self):
        teacher = self.create_user('teacher', 'TEACHER')
        learner = self.create_user('learner', 'STUDENT')
        other_learner = self.create_user('other_learner', 'STUDENT')
        grade_three_quest = self.create_quest(teacher)
        grade_four_quest = self.create_quest(
            teacher,
            title='A Grade Four Quest',
            grade_level=4,
        )
        unpublished_quest = self.create_quest(
            teacher,
            title='A Draft Quest',
            is_published=False,
        )
        QuestAttempt.objects.create(
            learner=other_learner,
            quest=grade_three_quest,
            selected_answer='B',
            is_correct=True,
        )
        self.client.force_login(learner)

        quests_response = self.client.get(reverse('student_quests'))
        self.assertContains(quests_response, grade_three_quest.title)
        self.assertNotContains(quests_response, grade_four_quest.title)
        self.assertNotContains(quests_response, unpublished_quest.title)
        progress_response = self.client.get(reverse('student_progress'))
        self.assertNotContains(progress_response, grade_three_quest.title)
