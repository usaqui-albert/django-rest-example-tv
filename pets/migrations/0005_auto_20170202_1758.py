# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-02 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0004_auto_20161004_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='fixed',
            field=models.NullBooleanField(default=None),
        ),
    ]