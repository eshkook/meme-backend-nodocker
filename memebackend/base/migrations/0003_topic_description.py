# Generated by Django 4.2.5 on 2023-09-29 14:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0002_topic"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
