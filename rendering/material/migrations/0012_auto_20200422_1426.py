# Generated by Django 3.0 on 2020-04-22 11:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0011_auto_20200422_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),

        migrations.RemoveField(
            model_name='colormatch',
            name='texture',
        ),
        migrations.AddField(
            model_name='colormatch',
            name='finish',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='material.Finish'),
        ),
        migrations.AddField(
            model_name='finish',
            name='color',
            field=models.CharField(help_text='HEX color, as #RRGGBB', max_length=7, null=True, verbose_name='Color'),
        ),
        migrations.AddField(
            model_name='finish',
            name='metalness',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='name',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='normal',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='roughness',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='specular',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='squ',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='finish',
            name='transparency',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='colormatch',
            name='chart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='material.ColorMatchingChart'),
        ),
        migrations.AlterField(
            model_name='finish',
            name='url',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
