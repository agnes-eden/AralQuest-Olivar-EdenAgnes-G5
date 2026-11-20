from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
    ]
    GRADE_CHOICES = [
        (3, 'Grade 3'),
        (4, 'Grade 4'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    grade_level = models.SmallIntegerField(choices=GRADE_CHOICES, null=True, blank=True)
    school_name = models.CharField(max_length=150, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        constraints = [
            models.CheckConstraint(
                condition=Q(role__in=['STUDENT', 'TEACHER']),
                name='valid_user_role'
            ),
            models.CheckConstraint(
                condition=Q(grade_level__in=[3, 4]) | Q(grade_level__isnull=True),
                name='valid_grade_level'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class LearningQuest(models.Model):
    SUBJECT_CHOICES = [
        ('READING', 'Reading'),
        ('LANGUAGE', 'Language'),
        ('MATH', 'Math'),
    ]
    GRADE_CHOICES = UserProfile.GRADE_CHOICES
    ANSWER_CHOICES = [
        ('A', 'Choice A'),
        ('B', 'Choice B'),
        ('C', 'Choice C'),
        ('D', 'Choice D'),
    ]

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_quests',
    )
    title = models.CharField(max_length=120)
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICES)
    grade_level = models.SmallIntegerField(choices=GRADE_CHOICES)
    question = models.TextField()
    choice_a = models.CharField(max_length=200)
    choice_b = models.CharField(max_length=200)
    choice_c = models.CharField(max_length=200)
    choice_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def answer_options(self):
        return (
            ('A', self.choice_a),
            ('B', self.choice_b),
            ('C', self.choice_c),
            ('D', self.choice_d),
        )


class QuestAttempt(models.Model):
    learner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_quest_attempts',
    )
    quest = models.ForeignKey(
        LearningQuest,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    selected_answer = models.CharField(max_length=1, choices=LearningQuest.ANSWER_CHOICES)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('learner', 'quest'),
                name='one_latest_attempt_per_learner_quest',
            ),
        ]

    def __str__(self):
        return f"{self.learner.username}: {self.quest.title}"