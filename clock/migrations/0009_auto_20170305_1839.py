# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-05 18:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clock', '0008_auto_20170305_1837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='avatarSource_text',
            new_name='avatar_source_text',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='displayName_text',
            new_name='display_name_text',
        ),
    ]
