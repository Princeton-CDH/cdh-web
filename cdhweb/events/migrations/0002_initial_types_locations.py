# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_initial_types_locations(apps, schema_editor):
    EventType = apps.get_model("events", "EventType")
    Location = apps.get_model("events", "Location")

    for evt_type in [
        "Workshop",
        "Guest Lecture",
        "Reception",
        "Reading Group",
        "Panel",
        "Deadline",
        "Working Group",
        "Symposium",
    ]:
        EventType.objects.create(name=evt_type)

    Location.objects.create(
        name="Center for Digital Humanities",
        short_name="CDH",
        address="Firestone Library, Floor B",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_types_locations, reverse_code=migrations.RunPython.noop
        ),
    ]
