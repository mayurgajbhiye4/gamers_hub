# Generated by Django 5.1.2 on 2024-11-12 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0013_remove_userprofile_following_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='network.userprofile'),
        ),
    ]
