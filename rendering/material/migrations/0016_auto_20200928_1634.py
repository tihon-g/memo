# Generated by Django 3.0 on 2020-09-28 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0015_auto_20200928_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='pattern',
            name='design',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='pattern',
            name='squ',
            field=models.CharField(max_length=16, null=True),
        ),
    ]
