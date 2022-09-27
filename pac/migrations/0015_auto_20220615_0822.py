# Generated by Django 2.1.13 on 2022-06-15 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pac', '0014_auto_20220608_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='basingpoint',
            name='terminal_id',
            field=models.ForeignKey(db_column='TerminalID', null=True, on_delete=django.db.models.deletion.CASCADE, to='pac.Terminal'),
        ),
        migrations.AddField(
            model_name='postalcode',
            name='province_id',
            field=models.ForeignKey(db_column='ProvinceID', null=True, on_delete=django.db.models.deletion.CASCADE, to='pac.Province'),
        ),
        migrations.AddField(
            model_name='servicepoint',
            name='terminal_id',
            field=models.ForeignKey(db_column='TerminalID', null=True, on_delete=django.db.models.deletion.CASCADE, to='pac.Terminal'),
        ),
        migrations.AlterField(
            model_name='servicepoint',
            name='basing_point',
            field=models.ForeignKey(db_column='BasingPointID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='pac.BasingPoint'),
        ),
    ]