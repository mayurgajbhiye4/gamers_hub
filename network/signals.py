from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from .models import *
from django.contrib.auth.models import User
import requests
from decouple import config

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(m2m_changed, sender=Post.likes.through)
def send_like_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":  # Triggered when a like is added
        for user_id in pk_set:  # `pk_set` contains the IDs of users who liked the post
            user = User.objects.get(pk=user_id)

            if instance.author == user:
                continue

            Notification.objects.create(
                user=instance.author,
                sender_id=user_id,
                notification_type="like",
                content_object=instance,
            )


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:

        if instance.post.author == instance.user:
            return
        
        Notification.objects.create(
            user=instance.post.author,
            sender=instance.user,
            notification_type="comment",
            content_object=instance.post,
        )


@receiver(post_save, sender=Follower)
def send_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.followed_user,
            sender=instance.user,
            notification_type="follow",
        )

@receiver(m2m_changed, sender=UserProfile.bookmarks.through)
def send_bookmark_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":  # When a post is bookmarked
        for post_id in pk_set:
            post = Post.objects.get(pk=post_id)  # Ensure this is a Post instance

            if post.author == instance.user:  # Skip if the author is the same as the user
                continue

            Notification.objects.create(
                user=post.author,  # The post author
                sender=instance.user,  # The user who bookmarked the post
                notification_type="bookmark",
                post=post,
                content_object=post
            )


@receiver(pre_save, sender=GameZone)
def fetch_game_image(sender, instance, **kwargs):
    RAWG_API_KEY = config('RAWG_API_KEY')
    if not instance.image_url:
        response = requests.get(f'https://api.rawg.io/api/games?search={instance.title}&key=RAWG_API_KEY')
        if response.status_code == 200:
            data = response.json()
            instance.image_url = data['results'][0]['background_image'] if data['results'] else None