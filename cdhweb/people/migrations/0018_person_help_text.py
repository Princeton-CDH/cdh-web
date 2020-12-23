# Generated by Django 2.2.17 on 2020-12-23 19:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0017_profile_phone_office_to_person'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name_plural': 'people'},
        ),
        migrations.AlterField(
            model_name='person',
            name='department',
            field=models.CharField(blank=True, help_text='Academic Department at Princeton or other institution', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='office_location',
            field=models.CharField(blank=True, help_text='Office number and building', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Office phone number', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(help_text='Corresponding user account for this person (optional)', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='CDH staff or Postdoctoral Fellow. If checked, person will be listed on the CDH staff page and will have a profile page on the site.'),
        ),
    ]