# Generated by Django 3.2.8 on 2021-10-19 01:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0021_auto_20211018_2206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='description',
            new_name='descripcion',
        ),
    ]