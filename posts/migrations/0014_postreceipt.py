# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-09 20:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0013_post_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transacction_id', models.CharField(max_length=200)),
                ('receipt', models.CharField(blank=True, max_length=1200, null=True)),
                ('developerPayload', models.CharField(blank=True, max_length=50, null=True)),
                ('purchaseToken', models.CharField(blank=True, max_length=50, null=True)),
                ('store', models.CharField(blank=True, choices=[(b'apple', b'App Store.'), (b'google', b'Play Store.')], max_length=50, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]