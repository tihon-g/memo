# Generated by Django 2.2.5 on 2019-10-07 12:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0011_model3d_shadow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combinemats',
            name='composition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='furniture.Composition'),
        ),
        migrations.AlterField(
            model_name='model3d',
            name='name',
            field=models.FileField(null=True, upload_to='static/furniture/models'),
        ),
    ]
