# Generated by Django 2.0 on 2020-04-21 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_foundry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extrusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('press_code', models.CharField(max_length=50, null=True)),
                ('shift_code', models.CharField(max_length=50, null=True)),
                ('maint_down_time', models.FloatField(blank=True, default=0, null=True)),
                ('other_down_time', models.FloatField(blank=True, default=0, null=True)),
                ('headcount', models.IntegerField(blank=True, null=True)),
                ('net_lbs_extruded', models.FloatField(blank=True, default=0, null=True)),
                ('gross_lbs_extruded', models.FloatField(blank=True, default=0, null=True)),
                ('percent_attainment', models.FloatField(blank=True, default=0, null=True)),
                ('safety_comments', models.TextField(blank=True)),
                ('overrun_comments', models.TextField(blank=True)),
                ('out_of_tolerance_comments', models.TextField(blank=True)),
                ('surface_defects_comments', models.TextField(blank=True)),
                ('cooling_defects_comments', models.TextField(blank=True)),
                ('handling_defects_comments', models.TextField(blank=True)),
                ('attempted_die_runs', models.IntegerField(blank=True, null=True)),
                ('successful_die_runs', models.IntegerField(blank=True, null=True)),
                ('plugged_run', models.IntegerField(blank=True, null=True)),
                ('dimensional_run', models.IntegerField(blank=True, null=True)),
                ('finished_run', models.IntegerField(blank=True, null=True)),
                ('broken_run', models.IntegerField(blank=True, null=True)),
                ('run_attainment_percent', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
    ]
