# Generated by Django 3.0 on 2019-12-14 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0013_auto_20191205_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='model3d',
            name='shadow',
        ),
    ]
