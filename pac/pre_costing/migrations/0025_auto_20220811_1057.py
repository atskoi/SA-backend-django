# Generated by Django 2.1.13 on 2022-08-11 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pre_costing', '0024_auto_20220810_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockroutehistory',
            name='is_exclude_destination',
            field=models.BooleanField(db_column='IsExcludeDestination', default=False),
        ),
        migrations.AddField(
            model_name='dockroutehistory',
            name='is_exclude_source',
            field=models.BooleanField(db_column='IsExcludeSource', default=False),
        ),
    ]