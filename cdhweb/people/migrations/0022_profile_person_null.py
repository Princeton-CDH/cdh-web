# Generated by Django 2.2.17 on 2021-01-07 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0021_peoplelandingpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepage',
            name='person',
            field=models.OneToOneField(help_text='Corresponding person for this profile', null=True, on_delete=models.deletion.SET_NULL, to='people.Person'),
        ),
    ]