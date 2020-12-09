# Generated by Django 3.1 on 2020-11-07 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0023_auto_20201105_1726'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machine',
            old_name='ready',
            new_name='working',
        ),
        migrations.AddField(
            model_name='machine',
            name='lastRender',
            field=models.DateTimeField(null=True),
        ),
    ]
