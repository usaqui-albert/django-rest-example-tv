# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-26 22:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pets.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('fixed', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to=pets.models.uploads_path)),
                ('age', models.IntegerField()),
                ('pet_type', models.CharField(max_length=150)),
                ('breed', models.CharField(max_length=150)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pet',
                'verbose_name_plural': 'Pets',
            },
        ),
    ]
