# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-21 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_profileimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='blur_images',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='comments_like_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='comments_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='interested_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='vet_reply_notification',
            field=models.BooleanField(default=False),
        ),
    ]
