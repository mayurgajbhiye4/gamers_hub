# Generated by Django 5.1.2 on 2024-12-01 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0016_remove_userprofile_following'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Following',
        ),
    ]
