# Generated by Django 2.2.4 on 2019-08-22 23:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0005_auto_20190823_0027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='date',
            field=models.DateField(default=datetime.date(2019, 8, 23)),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
