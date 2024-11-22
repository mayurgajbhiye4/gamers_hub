from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signUp, name='signup'),
    path('', include('django.contrib.auth.urls')),

    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/followers/', views.followers, name='followers'),
    path('profile/<str:username>/following/', views.following, name='following'),
    
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),
    
    path('create_post/', views.create_post, name='create_post'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),

    path('fetch-new-posts/', views.fetch_new_posts, name='fetch_new_posts'),

    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/add_comment/', views.add_comment, name="add_comment"),

    path('bookmark/<int:post_id>/', views.bookmark_post, name='bookmark_post'),
    path('bookmarks/', views.view_bookmarks, name='view_bookmarks'),
    path('unbookmark/<int:post_id>/', views.unbookmark_post, name='unbookmark_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)