# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-24 00:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20170206_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='comments_like_notification',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='comments_notification',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='interested_notification',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='vet_reply_notification',
            field=models.BooleanField(default=True),
        ),
    ]
