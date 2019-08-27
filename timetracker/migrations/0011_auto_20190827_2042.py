# Generated by Django 2.2.4 on 2019-08-27 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0010_auto_20190823_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checking',
            name='check',
        ),
        migrations.RemoveField(
            model_name='checking',
            name='time',
        ),
        migrations.AddField(
            model_name='checking',
            name='checkin',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='checking',
            name='checkout',
            field=models.DateTimeField(blank=True, default=None),
        ),
        migrations.DeleteModel(
            name='WorkingHours',
        ),
    ]