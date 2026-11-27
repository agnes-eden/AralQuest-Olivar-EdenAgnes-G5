from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_learningquest_questattempt'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='questattempt',
            name='one_latest_attempt_per_learner_quest',
        ),
    ]
