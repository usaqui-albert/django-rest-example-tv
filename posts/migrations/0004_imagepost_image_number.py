# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-25 21:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_paymentamount'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagepost',
            name='image_number',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)], default=1),
        ),
    ]