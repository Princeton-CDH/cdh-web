# Generated by Django 5.0.5 on 2024-06-05 03:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_project_project_website'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectslandingpage',
            name='attachments',
        ),
        migrations.RemoveField(
            model_name='projectslandingpage',
            name='body',
        ),
    ]
