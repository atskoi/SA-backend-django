# Generated by Django 2.1.13 on 2022-09-07 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rrf', '0134_merge_20220907_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessorialdetailhistory',
            name='acc_header_version_id',
            field=models.BigIntegerField(db_column='AccountHeader', default=None),
        ),
    ]