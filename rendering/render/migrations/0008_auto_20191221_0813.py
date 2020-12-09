# Generated by Django 3.0 on 2019-12-21 08:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0007_iteration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='angles',
        ),
        migrations.RemoveField(
            model_name='order',
            name='session',
        ),
        migrations.AddField(
            model_name='iteration',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='render.Order'),
        ),
        migrations.AddField(
            model_name='order',
            name='angle_0',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='angle_3',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='focus',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='size_x',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='size_y',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
