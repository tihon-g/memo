# Generated by Django 3.1 on 2020-11-15 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0019_delete_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pattern',
            name='by',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='copyrights',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='design',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='squ',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='vendor',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='web',
            field=models.URLField(blank=True, max_length=128, null=True),
        ),
    ]
