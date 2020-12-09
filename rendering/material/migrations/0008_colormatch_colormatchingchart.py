import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0007_auto_20191015_0834'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorMatchingChart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ColorMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suited', models.CharField(max_length=2048, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('chart', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='material.ColorMatchingChart')),
                ('texture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='material.Texture')),
            ],
        ),
    ]
