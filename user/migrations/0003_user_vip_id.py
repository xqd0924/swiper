# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2020-05-22 15:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200515_2321'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='vip_id',
            field=models.IntegerField(default=1, verbose_name='Vip ID'),
        ),
    ]