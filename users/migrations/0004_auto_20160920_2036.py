# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-20 20:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160920_1551'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VeterinarianAreaInterest',
            new_name='AreaInterest',
        ),
        migrations.AlterModelOptions(
            name='areainterest',
            options={'ordering': ('id',)},
        ),
    ]
