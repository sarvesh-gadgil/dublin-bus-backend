# Generated by Django 3.0.7 on 2020-06-30 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bus_stops', '0001_initial'),
        ('stops_routes', '0002_auto_20200627_1738'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stopsroutes',
            unique_together={('stop_id', 'route', 'program_number')},
        ),
    ]
