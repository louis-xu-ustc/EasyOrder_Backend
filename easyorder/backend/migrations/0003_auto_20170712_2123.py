# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20170709_2335'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='dish',
            name='rateNum',
        ),
        migrations.AlterField(
            model_name='dish',
            name='photo',
            field=models.ImageField(upload_to=b'dishes'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='vote',
            name='dish',
            field=models.ForeignKey(related_name='vote', to='backend.Dish'),
        ),
        migrations.AddField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(related_name='vote', to='backend.User'),
        ),
    ]
