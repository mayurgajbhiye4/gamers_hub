from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signUp, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('following/', views.following, name='following'),  
    path('followers/', views.followers, name='followers'),  
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create_post/', views.create_post, name='create_post'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('view/<int:post_id>/', views.view_post, name='view_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)