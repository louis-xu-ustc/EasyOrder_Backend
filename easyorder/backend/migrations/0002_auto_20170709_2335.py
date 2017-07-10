# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
                ('photo', models.ImageField(upload_to=b'cars')),
                ('rate', models.FloatField()),
                ('rateNum', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField()),
                ('paid', models.BooleanField()),
                ('dish', models.ForeignKey(related_name='order', to='backend.Dish')),
            ],
        ),
        migrations.RenameField(
            model_name='user',
            old_name='token',
            new_name='twitterID',
        ),
        migrations.AddField(
            model_name='location',
            name='name',
            field=models.CharField(default=b'Anonymous', max_length=100),
        ),
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(related_name='order', to='backend.User'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(related_name='notification', to='backend.User'),
        ),
    ]
