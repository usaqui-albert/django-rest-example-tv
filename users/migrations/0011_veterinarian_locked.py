# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-12 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20161121_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='veterinarian',
            name='locked',
            field=models.BooleanField(default=False),
        ),
    ]