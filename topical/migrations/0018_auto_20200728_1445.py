# Generated by Django 3.0.8 on 2020-07-28 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topical', '0017_auto_20200728_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_setup',
            field=models.BooleanField(),
        ),
    ]
