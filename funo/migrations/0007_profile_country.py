# Generated by Django 3.0.3 on 2020-03-23 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funo', '0006_remove_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
