# Generated by Django 5.1.2 on 2024-11-28 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0015_alter_comment_options_post_likes_delete_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='following',
        ),
    ]
