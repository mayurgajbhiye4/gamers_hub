from django.db import models
from django.contrib.auth.models import User, Group, Permission

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.author.username} - {self.text[:30]}" 
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    bookmarks = models.ManyToManyField(Post, related_name="bookmarked_by", blank=True)

    def __str__(self):
        return self.user.username 
    
    
class Follower(models.Model):
    user = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} follows {self.followed_user.username}"

    class Meta:
        unique_together = ('user', 'followed_user')


class Following(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Ensure a user can only follow another user once

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"
    
    

# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True)
#     actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actor", null=True)
#     notification_type = models.CharField(max_length=50)  # e.g., "like", "comment", "follow
#     content_object = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)


