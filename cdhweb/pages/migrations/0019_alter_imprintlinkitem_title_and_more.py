# Generated by Django 5.0.5 on 2024-05-14 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdhpages', '0018_remove_footercolumn_footer_contactlinksitem_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imprintlinkitem',
            name='title',
            field=models.CharField(max_length=60, verbose_name='link title'),
        ),
        migrations.AlterField(
            model_name='secondarynavigationctabutton',
            name='title',
            field=models.CharField(max_length=60, verbose_name='link title'),
        ),
        migrations.AlterField(
            model_name='secondarynavigationitem',
            name='title',
            field=models.CharField(max_length=60, verbose_name='link title'),
        ),
        migrations.AlterField(
            model_name='usefullinksitem',
            name='title',
            field=models.CharField(max_length=60, verbose_name='link title'),
        ),
    ]
