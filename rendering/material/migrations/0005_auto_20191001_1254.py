# Generated by Django 2.1.4 on 2019-10-01 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0004_texture_archive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='texture',
            name='code',
        ),
        migrations.RemoveField(
            model_name='texture',
            name='info',
        ),
        migrations.RemoveField(
            model_name='texture',
            name='name',
        ),
        migrations.AlterField(
            model_name='texture',
            name='url',
            field=models.FilePathField(unique=True),
        ),
    ]
