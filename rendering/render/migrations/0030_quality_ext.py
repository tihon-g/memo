# Generated by Django 3.1 on 2020-12-04 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0029_quality_engine'),
    ]

    operations = [
        migrations.AddField(
            model_name='quality',
            name='ext',
            field=models.CharField(choices=[('jpg', 'JPEG'), ('png', 'PNG')], default='jpg', max_length=13),
        ),
    ]
