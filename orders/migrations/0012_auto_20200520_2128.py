# Generated by Django 2.0 on 2020-05-21 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20200520_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ASN_contact',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='ASN_title',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
