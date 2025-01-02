# Generated by Django 5.1.2 on 2025-01-02 20:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_events_members"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="events",
            name="members",
        ),
        migrations.AddField(
            model_name="events",
            name="members",
            field=models.ManyToManyField(
                related_name="invitedusers", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]