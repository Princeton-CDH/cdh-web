# Generated by Django 5.0.14 on 2025-05-02 02:30

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_alter_event_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventslandingpage',
            name='preface',
            field=wagtail.fields.RichTextField(blank=True, help_text='\n            Text that sits between the description and the child-page listing\n        '),
        ),
    ]
