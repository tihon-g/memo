# Generated by Django 2.2.5 on 2019-10-03 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0005_auto_20191001_1254'),
        ('furniture', '0007_auto_20191003_1306'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='combine_mats',
            new_name='CombineMats',
        ),
    ]
