# Generated by Django 2.0 on 2020-05-21 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_auto_20200521_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='line',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
