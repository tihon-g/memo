# Generated by Django 3.0 on 2019-12-16 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0015_auto_20191216_1118'),
        ('render', '0006_auto_20191211_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='Iteration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mats', models.CharField(max_length=2048)),
                ('parts', models.ManyToManyField(to='furniture.Part')),
            ],
        ),
    ]
