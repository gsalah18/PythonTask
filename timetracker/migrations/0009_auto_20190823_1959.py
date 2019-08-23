# Generated by Django 2.2.4 on 2019-08-23 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetracker', '0008_auto_20190823_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='date',
            field=models.DateField(),
        ),
        migrations.CreateModel(
            name='WorkingHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours', models.IntegerField()),
                ('date', models.DateField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetracker.Employee')),
            ],
        ),
    ]