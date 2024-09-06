# Generated by Django 5.0.8 on 2024-09-03 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdhpages', '0060_alter_contentpage_body_alter_homepage_body_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purplemode',
            name='site',
        ),
        migrations.AlterField(
            model_name='purplemode',
            name='purple_mode',
            field=models.BooleanField(default=False, help_text='\n            This will turn the site purple by transforming\n            all shades of cyan on the site into shades of\n            purple\n        '),
        ),
    ]
