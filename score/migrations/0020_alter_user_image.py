# Generated by Django 3.2.8 on 2021-10-15 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0019_alter_score_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
