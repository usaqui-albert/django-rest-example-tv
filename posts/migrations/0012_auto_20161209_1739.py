# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-09 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20161208_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, b'offensive'), (2, b'not relevant'), (3, b'spam')]),
        ),
    ]
