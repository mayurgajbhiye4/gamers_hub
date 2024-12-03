from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Comment)

class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'created_at')
    search_fields = ('user__username', 'followed_user__username')
    list_filter = ('created_at',)

admin.site.register(Follower, FollowerAdmin)