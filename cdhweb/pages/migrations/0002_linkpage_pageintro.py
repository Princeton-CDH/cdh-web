# Generated by Django 2.2.17 on 2021-01-13 23:17

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('cdhpages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('link_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='link to a custom URL')),
                ('url_append', models.CharField(blank=True, help_text='Use this to optionally append a #hash or querystring to the URL.', max_length=255, verbose_name='append to URL')),
                ('extra_classes', models.CharField(blank=True, help_text='Optionally specify css classes to be added to this page when it appears in menus.', max_length=100, verbose_name='menu item css classes')),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page', verbose_name='link to an internal page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='PageIntro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paragraph', wagtail.core.fields.RichTextField()),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cdhpages.LinkPage')),
            ],
        ),
    ]