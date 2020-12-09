# Generated by Django 3.1 on 2020-12-04 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0021_auto_20201204_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finish',
            name='maps',
        ),
        migrations.AlterField(
            model_name='features',
            name='name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='finish',
            name='name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='finish',
            name='pattern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='material.pattern'),
        ),
        migrations.AlterField(
            model_name='finish',
            name='tile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='material.tile'),
        ),
        migrations.AlterField(
            model_name='hsv',
            name='name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='tile',
            name='name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
