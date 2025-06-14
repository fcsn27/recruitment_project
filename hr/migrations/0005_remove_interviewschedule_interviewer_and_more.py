# Generated by Django 5.2.1 on 2025-05-30 14:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hr", "0004_actionlog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="interviewschedule",
            name="interviewer",
        ),
        migrations.AddField(
            model_name="interviewschedule",
            name="interviewers",
            field=models.ManyToManyField(
                related_name="interviews", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
