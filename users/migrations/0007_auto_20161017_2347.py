# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-17 23:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20161013_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ForeignKey(blank=True, default=1, help_text='The group this user belongs to. A user will get all permissions granted to his group.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
    ]
