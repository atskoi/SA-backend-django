# Generated by Django 2.1.13 on 2021-03-19 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pac', '0007_notification_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='external_city_name',
            field=models.CharField(blank=True, db_column='ExternalCityName', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='external_erp_id',
            field=models.CharField(blank=True, db_column='ExternalERPID', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='external_city_name',
            field=models.CharField(blank=True, db_column='ExternalCityName', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='accounthistory',
            name='external_erp_id',
            field=models.CharField(blank=True, db_column='ExternalERPID', max_length=100, null=True),
        ),
    ]