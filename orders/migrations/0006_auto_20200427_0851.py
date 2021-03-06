# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2020-04-27 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_extrusion'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='amount_received',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
