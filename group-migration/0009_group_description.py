# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-26 12:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]