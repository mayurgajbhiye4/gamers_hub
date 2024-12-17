from .models import Notification
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def base_view(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Return a dictionary containing unread notifications
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).exists()
        return {'unread_notifications': unread_notifications}
    
    # If the user is not authenticated, return an empty dictionary
    return {}