# Generated by Django 5.2.1 on 2025-05-17 13:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0004_jobrequest_rejection_reason_alter_application_job_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="jobrequest",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="jobrequest",
            name="status",
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="actionlog",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="actionlog",
            name="job_request",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="action_logs",
                to="jobs.jobrequest",
            ),
        ),
        migrations.AlterField(
            model_name="jobrequest",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="jobrequest",
            name="rejection_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="jobrequest",
            name="title",
            field=models.CharField(max_length=200),
        ),
    ]
