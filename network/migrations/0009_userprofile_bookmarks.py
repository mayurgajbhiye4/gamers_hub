# Generated by Django 5.1.2 on 2024-11-07 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_remove_comment_author_remove_comment_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bookmarks',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_by', to='network.post'),
        ),
    ]
