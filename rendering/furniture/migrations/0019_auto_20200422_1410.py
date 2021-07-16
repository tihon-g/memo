# Generated by Django 3.0 on 2020-04-22 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0011_auto_20200422_1410'),
        ('furniture', '0018_auto_20200312_2128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mesh',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('optional', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('producer', models.CharField(max_length=32)),
                ('product_code', models.CharField(blank='', max_length=32, null=True)),
                ('type', models.CharField(choices=[('table', 'Table'), ('chair', 'Chair'), ('toy', 'Toy')], max_length=5)),
                ('collection', models.CharField(max_length=32)),
                ('swatch', models.ImageField(blank=True, null=True, upload_to='/static/furniture/swatches')),
            ],
        ),
        migrations.CreateModel(
            name='ProductKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('comment', models.CharField(max_length=128)),
            ],
        ),
        migrations.RenameField(
            model_name='part',
            old_name='colorchart',
            new_name='colorChart',
        ),
        migrations.RemoveField(
            model_name='model3d',
            name='created',
        ),
        migrations.RemoveField(
            model_name='model3d',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='model3d',
            name='item',
        ),
        migrations.RemoveField(
            model_name='model3d',
            name='url',
        ),
        migrations.RemoveField(
            model_name='part',
            name='model',
        ),
        migrations.AddField(
            model_name='model3d',
            name='blend',
            field=models.FileField(blank=True, null=True, upload_to='static/furniture/models/blender'),
        ),
        migrations.AddField(
            model_name='model3d',
            name='glb',
            field=models.FileField(null=True, upload_to='static/furniture/models/gltf'),
        ),
        migrations.AddField(
            model_name='model3d',
            name='solidSource',
            field=models.FileField(blank=True, null=True, upload_to='static/furniture/models/sw'),
        ),
        migrations.AlterField(
            model_name='part',
            name='cover',
            field=models.ManyToManyField(blank=True, to='material.Nature'),
        ),
        migrations.AlterField(
            model_name='part',
            name='name',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.AddField(
            model_name='productkind',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='furniture.Model3D'),
        ),
        migrations.AddField(
            model_name='productkind',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='furniture.Product'),
        ),
        migrations.AddField(
            model_name='mesh',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='furniture.Model3D'),
        ),
        migrations.AddField(
            model_name='part',
            name='meshes',
            field=models.ManyToManyField(blank=True, to='furniture.Mesh'),
        ),
        migrations.AddField(
            model_name='part',
            name='variant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='furniture.ProductKind'),
        ),
    ]
