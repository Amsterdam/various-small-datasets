# Generated by Django 2.1.7 on 2019-04-10 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='geometry_epsg',
            field=models.IntegerField(choices=[(4326, 4326), (28992, 28992)], null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='geometry_type',
            field=models.CharField(choices=[('POINT', 'POINT'), ('POLYGON', 'POLYGON'), ('LINE', 'LINE')], max_length=32),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='geometry_type',
            field=models.CharField(choices=[('POINT', 'POINT'), ('POLYGON', 'POLYGON'), ('LINE', 'LINE')], max_length=32, null=True),
        ),
    ]
