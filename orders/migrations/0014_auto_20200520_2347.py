# Generated by Django 2.0 on 2020-05-21 03:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_auto_20200520_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.TextField(blank=True)),
                ('customer_number', models.IntegerField()),
                ('active', models.IntegerField(default='1')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='bill_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='ship_address',
        ),
        migrations.AddField(
            model_name='order',
            name='customer_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.CustomerName'),
        ),
    ]
