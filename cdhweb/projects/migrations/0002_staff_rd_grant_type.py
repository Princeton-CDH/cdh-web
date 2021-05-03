# Generated by Django 2.2.19 on 2021-05-03 16:56

from django.db import migrations


def create_staff_rd_grant_type(apps, schema_editor):
    # create Staff R&D and postdoc grant types if they do not already exist
    GrantType = apps.get_model('projects', 'GrantType')
    GrantType.objects.get_or_create(grant_type='Staff R&D')
    GrantType.objects.get_or_create(grant_type='Postdoctoral Research Project')


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_staff_rd_grant_type,
                             reverse_code=migrations.RunPython.noop),
    ]
