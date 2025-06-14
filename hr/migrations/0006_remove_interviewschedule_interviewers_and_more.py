# Generated by Django 5.2.1 on 2025-05-31 07:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hr", "0005_remove_interviewschedule_interviewer_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="interviewschedule",
            name="interviewers",
        ),
        migrations.RemoveField(
            model_name="interviewschedule",
            name="notes",
        ),
        migrations.AddField(
            model_name="interviewschedule",
            name="department",
            field=models.CharField(
                choices=[
                    ("IT", "Công nghệ thông tin"),
                    ("HR", "Nhân sự"),
                    ("Finance", "Tài chính"),
                    ("Marketing", "Marketing"),
                ],
                default="IT",
                help_text="Phòng ban phỏng vấn",
                max_length=100,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="interviewschedule",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
