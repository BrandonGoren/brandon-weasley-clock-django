# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-07 03:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clock', '0011_auto_20170506_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationcondition',
            name='place_name',
            field=models.CharField(default='Randolph', max_length=100),
            preserve_default=False,
        ),
    ]
