# Generated by Django 4.1.2 on 2022-11-21 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webscraper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviedata',
            name='rating',
            field=models.FloatField(),
        ),
    ]
