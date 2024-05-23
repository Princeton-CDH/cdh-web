# Generated by Django 5.0.5 on 2024-05-14 08:29

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cdhpages", "0019_alter_imprintlinkitem_title_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SocialMediaLinks",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site",
                    models.CharField(
                        choices=[
                            ("facebook", "Facebook"),
                            ("instagram", "Instagram"),
                            ("twitter", "Twitter"),
                            ("github", "Github"),
                        ]
                    ),
                ),
                ("url", models.URLField()),
                (
                    "social_media_link",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_media_links",
                        to="cdhpages.footer",
                    ),
                ),
            ],
        ),
    ]