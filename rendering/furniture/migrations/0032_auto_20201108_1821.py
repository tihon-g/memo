# Generated by Django 3.1 on 2020-11-08 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0031_auto_20201031_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
