# Generated by Django 5.1.2 on 2025-01-03 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_alter_events_event_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="events",
            name="event_image",
            field=models.ImageField(
                blank=True, default="default.jpg", null=True, upload_to="event_images"
            ),
        ),
    ]
