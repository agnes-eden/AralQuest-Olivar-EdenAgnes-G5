import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningQuest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('subject', models.CharField(choices=[('READING', 'Reading'), ('LANGUAGE', 'Language'), ('MATH', 'Math')], max_length=10)),
                ('grade_level', models.SmallIntegerField(choices=[(3, 'Grade 3'), (4, 'Grade 4')])),
                ('question', models.TextField()),
                ('choice_a', models.CharField(max_length=200)),
                ('choice_b', models.CharField(max_length=200)),
                ('choice_c', models.CharField(max_length=200)),
                ('choice_d', models.CharField(max_length=200)),
                ('correct_answer', models.CharField(choices=[('A', 'Choice A'), ('B', 'Choice B'), ('C', 'Choice C'), ('D', 'Choice D')], max_length=1)),
                ('is_published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_quests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='QuestAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_answer', models.CharField(choices=[('A', 'Choice A'), ('B', 'Choice B'), ('C', 'Choice C'), ('D', 'Choice D')], max_length=1)),
                ('is_correct', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_quest_attempts', to=settings.AUTH_USER_MODEL)),
                ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='accounts.learningquest')),
            ],
            options={
                'ordering': ('-updated_at',),
                'constraints': [
                    models.UniqueConstraint(fields=('learner', 'quest'), name='one_latest_attempt_per_learner_quest'),
                ],
            },
        ),
    ]
