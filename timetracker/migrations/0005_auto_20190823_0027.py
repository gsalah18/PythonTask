# Generated by Django 2.2.4 on 2019-08-22 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0004_auto_20190822_2300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checking',
            old_name='user',
            new_name='employee',
        ),
        migrations.RenameField(
            model_name='vacation',
            old_name='user',
            new_name='employee',
        ),
    ]