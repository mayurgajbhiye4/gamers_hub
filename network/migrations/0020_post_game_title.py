# Generated by Django 5.1.2 on 2024-12-14 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0019_notification_content_type_notification_object_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='game_title',
            field=models.CharField(default='Unknown Game', max_length=100),
        ),
    ]
