# Generated by Django 5.0.5 on 2024-06-05 02:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0012_rename_eventslinkpage_eventslinkpagearchived_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventslandingpage",
            name="attachments",
        ),
        migrations.RemoveField(
            model_name="eventslandingpage",
            name="body",
        ),
    ]
