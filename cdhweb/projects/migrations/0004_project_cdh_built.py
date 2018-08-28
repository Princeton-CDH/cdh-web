# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-13 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_attachments_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='cdh_built',
            field=models.BooleanField(default=False, help_text='Project built by CDH Development & Design team.', verbose_name='CDH Built'),
        ),
    ]