# Generated by Django 3.0 on 2019-12-25 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0010_auto_20191219_1942'),
        ('furniture', '0015_auto_20191216_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='colorchart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='material.ColorMatchingChart'),
        ),
    ]
