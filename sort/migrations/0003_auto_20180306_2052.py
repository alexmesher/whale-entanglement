# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-06 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sort', '0002_photo_term'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='photos',
        ),
        migrations.AddField(
            model_name='tag',
            name='photo_sorted',
            field=models.ManyToManyField(to='sort.Photo_sorted'),
        ),
    ]
