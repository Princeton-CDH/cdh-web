# Generated by Django 5.0.5 on 2024-06-03 23:38

import wagtail.documents.blocks
import wagtail.fields
import wagtail.snippets.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0013_peoplelandingpage_disable_sidebar_alter_profile_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='peoplelandingpage',
            name='attachments',
            field=wagtail.fields.StreamField([('document', wagtail.documents.blocks.DocumentChooserBlock()), ('link', wagtail.snippets.blocks.SnippetChooserBlock('cdhpages.ExternalAttachment'))], blank=True, use_json_field=True),
        ),
    ]