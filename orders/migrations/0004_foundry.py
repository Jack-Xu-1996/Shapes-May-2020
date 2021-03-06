# Generated by Django 2.0 on 2020-04-21 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200408_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='Foundry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('furnace_number', models.IntegerField(blank=True, null=True)),
                ('heat_number', models.IntegerField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('diameter', models.IntegerField(blank=True, null=True)),
                ('alloy', models.IntegerField(blank=True, null=True)),
                ('cast_qty', models.IntegerField(blank=True, null=True)),
                ('total_weight', models.FloatField(blank=True, default=0, null=True)),
                ('degass', models.IntegerField(blank=True, null=True)),
                ('cast_shift', models.CharField(max_length=50, null=True)),
                ('cast_speed', models.IntegerField(blank=True, null=True)),
                ('Mg', models.FloatField(blank=True, default=0, null=True)),
                ('Si', models.FloatField(blank=True, default=0, null=True)),
                ('Fe', models.FloatField(blank=True, default=0, null=True)),
                ('Cu', models.FloatField(blank=True, default=0, null=True)),
                ('Cr', models.FloatField(blank=True, default=0, null=True)),
                ('Mn', models.FloatField(blank=True, default=0, null=True)),
                ('Zn', models.FloatField(blank=True, default=0, null=True)),
                ('Ti', models.FloatField(blank=True, default=0, null=True)),
                ('Bo', models.FloatField(blank=True, default=0, null=True)),
                ('Mg_HL', models.CharField(max_length=50, null=True)),
                ('Si_HL', models.CharField(max_length=50, null=True)),
                ('Fe_HL', models.CharField(max_length=50, null=True)),
                ('Cu_HL', models.CharField(max_length=50, null=True)),
                ('Cr_HL', models.CharField(max_length=50, null=True)),
                ('Mn_HL', models.CharField(max_length=50, null=True)),
                ('Zn_HL', models.CharField(max_length=50, null=True)),
                ('Ti_HL', models.CharField(max_length=50, null=True)),
                ('Bo_HL', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
