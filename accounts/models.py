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