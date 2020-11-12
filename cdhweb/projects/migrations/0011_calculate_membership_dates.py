# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-11-10 17:10
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.admin.models import CHANGE, DELETION
from django.contrib.contenttypes.management import create_contenttypes
from django.db import migrations
from django.core.exceptions import ObjectDoesNotExist


def calculate_membership_dates(apps, schema_editor):
    Membership = apps.get_model('projects', 'Membership')
    # get script user and log entry model to document changes
    User = apps.get_model('auth', 'User')
    script_user = User.objects.get(username=settings.SCRIPT_USERNAME)
    LogEntry = apps.get_model('admin', 'LogEntry')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # make sure content types are created before looking for one
    app_config = apps.get_app_config('projects')
    app_config.models_module = app_config.models_module or True
    create_contenttypes(app_config)
    membership_contenttype = ContentType.objects.get(
        app_label='projects', model='Membership')
    change_message = 'Set start and end dates based on associated grants'
    delete_message = 'Deleted consolidated membership'

    # sort by project, then user, then grant start date
    memberships = Membership.objects.all() \
                            .order_by('project', 'user', 'grant__start_date')

    # as we loop through, track current membership to extend across grants
    current = None
    for membership in memberships:
        if current:
            # if this membership matches the previous one, extend it
            if current.user == membership.user and \
               current.project == membership.project and \
               current.role == membership.role:
                # extend the end date
                current.end_date = calculate_membership_end(membership)
                # delete the obsolete membership
                membership.delete()
                # create log entry to document the deletion
                LogEntry.objects.log_action(
                    user_id=script_user.id,
                    content_type_id=membership_contenttype.pk,
                    object_id=membership.pk,
                    object_repr=str(membership),
                    change_message=delete_message,
                    action_flag=DELETION)

                continue

            # if it doesn't match, save it
            else:
                current.save()
                # create log entry to document the change
                LogEntry.objects.log_action(
                    user_id=script_user.id,
                    content_type_id=membership_contenttype.pk,
                    object_id=current.pk,
                    object_repr=str(current),
                    change_message=change_message,
                    action_flag=CHANGE)
                current = None

        if not current:
            # if there is no current membership to extend, start a new one
            current = membership
            # set dates based on associated grant & cdh position dates
            current.start_date = calculate_membership_start(membership)
            current.end_date = calculate_membership_end(membership)

    # save the last record after loop ends
    if current:
        current.save()
        # create log entry to document the change
        LogEntry.objects.log_action(
            user_id=script_user.id,
            content_type_id=membership_contenttype.pk,
            object_id=current.pk,
            object_repr=str(current),
            change_message=change_message,
            action_flag=CHANGE)

    # if any memberships are missing start dates, it will be a problem
    assert not Membership.objects.filter(start_date__isnull=True).exists()


def calculate_membership_start(membership):
    '''calculate membership start based on combination of
    associated grant dates and CDH position dates for CDH staff'''
    try:
        # staff should have positions, but handle if not
        if membership.user.profile.is_staff and \
           membership.user.positions.exists():
            # get the first start date for their time at CDH
            cdh_start = membership.user.positions.order_by('start_date')\
                .first().start_date
            return max(cdh_start, membership.grant.start_date)
    except ObjectDoesNotExist:
        # if user has no profile, they can't be cdh staff
        pass
    # otherwise, use grant start date
    return membership.grant.start_date


def calculate_membership_end(membership):
    '''calculate membership end based on combination of
    associated grant dates and CDH position dates for CDH staff'''

    # if override is set to current, mimic that behavior by returning
    # no end date (this will only work if current is set on the
    # *last* membership in a project)
    if membership.status_override == 'current':
        return None

    try:
        if membership.user.profile.is_staff and \
           membership.user.positions.exists():
            # get the end date for their most recent position at CDH
            cdh_end = membership.user.positions.order_by('start_date')\
                .last().end_date
            if cdh_end is not None:  # end date is None for current staff
                # if the grant has an end date, compare
                if membership.grant.end_date:
                    return min(cdh_end, membership.grant.end_date)
                # otherwise, use position end date
                return cdh_end
    except ObjectDoesNotExist:
        # if user has no profile, they can't be cdh staff
        pass

    # otherwise, use grant end date
    return membership.grant.end_date


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('projects', '0010_add_membership_date_range'),
        ('resources', '0005_create_script_user'),
        ('people', '0008_profile_slug_not_null'),
    ]

    operations = [
        migrations.RunPython(calculate_membership_dates,
                             reverse_code=migrations.RunPython.noop)
    ]
