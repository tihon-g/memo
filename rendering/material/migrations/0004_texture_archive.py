# Generated by Django 2.1.4 on 2019-09-30 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0003_auto_20190920_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='texture',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]
