from django.shortcuts import render,  redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, JsonResponse
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.exceptions import ValidationError
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.core import serializers
from django.utils.timezone import localtime
from django.urls import reverse
import requests 
from decouple import config
from django.core.cache import cache
from django.utils.text import slugify


def home(request):
    posts = list(Post.objects.all().order_by('-timestamp'))
    recommendations = get_profile_recommendations(request.user)

    user_profile = request.user.userprofile
    bookmarked_posts = [post.id for post in user_profile.bookmarks.all()]

    return render(request, 'home.html', 
                  {'posts': posts, 
                   'recommendations': recommendations,
                   'user_likes': {post.id: post.likes.count() for post in posts},
                   'bookmarked_posts': bookmarked_posts
                   })

def signUp(request):
    if request.method == "POST":    
        form = signupForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)   
            user.save()
            messages.info(request, "Account created successfully")
            return redirect('/signup/')
    else:
        form = signupForm()

    return render(request, "registration/signup.html", {'form':form})

@login_required(login_url='/login/')
def following(request, username):
    # Get the user whose "following" list is to be displayed
    user = get_object_or_404(User, username=username)

    # Get the users this user is following 
    following = Follower.objects.filter(user=user).select_related('followed_user')

    # Extract the profiles of the users being followed
    following_profiles = [follow.followed_user for follow in following]

    return render(request, 'following.html', {
        'user': user,
        'following_profiles': following_profiles
    })

@login_required(login_url='/login/') 
def followers(request, username):   
    user  = get_object_or_404(User, username=username) 
    profile_owner  = get_object_or_404(UserProfile, user=user)
    followers = Follower.objects.filter(followed_user=user)  

    followers_profiles = [f.user for f in followers]    

    return render(request, 'followers.html', {'profile_owner':profile_owner, 'followers': followers_profiles})


@login_required(login_url='/login/')
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    current_user = request.user

    if current_user == target_user:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself'}, status=400)

    # Check if the follow relationship already exists
    follow, created = Follower.objects.get_or_create(user=current_user, followed_user=target_user)

    if not created:
        # Unfollow if the relationship exists
        follow.delete()
        following = False
    else:
        # Follow if the relationship doesn't exist
        following = True

    # Return the updated follow state
    return JsonResponse({'success': True, 'following': following})

@login_required(login_url='/login/')
def profile(request, username):
    # Fetch the user profile based on the provided username
    profile_owner  = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get(user=profile_owner)

    # Fetch the user's posts, ordered by the latest first
    posts = Post.objects.filter(author=profile_owner).order_by('-timestamp')

    # Check if the logged-in user is viewing their own profile
    is_own_profile = request.user == profile_owner

    recommendations = get_profile_recommendations(request.user)

    is_following = Follower.objects.filter(user=request.user, followed_user=profile_owner).exists()

    bookmarked_posts = [post.id for post in user_profile.bookmarks.all()]

    # Context to pass to the template
    context = {
        'profile_owner': profile_owner,
        'user_profile': user_profile,
        'first_name': profile_owner.first_name,
        'last_name': profile_owner.last_name,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'recommendations': recommendations,
        'is_following': is_following,
        'bookmarked_posts': bookmarked_posts
    }

    return render(request, 'profile.html', context)

def validate_file_size(file, max_size):
    if file.size > max_size:
        raise ValidationError(f"File size exceeds {max_size / (1024 * 1024)} MB")


@login_required(login_url='/login/')
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        game_title = request.POST.get('game_title')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if image and video:
            # Handle the error (e.g., render the page with an error message)
            return render(request, 'create_post.html', {
                'error': 'Please upload either an image or a video, not both.'
            })

        # Validate file sizes
        if image:
            validate_file_size(image, max_size=20 * 1024 * 1024)  # 20MB limit
        if video:
            validate_file_size(video, max_size=200 * 1024 * 1024)  # 200MB limit

        # Save the post
        post = Post.objects.create(
            author=request.user,
            text=text,
            game_title=game_title,
            image=image,
            video=video
        )
        post.save()
        return redirect('home')  # Redirect to the homepage or another page

    return render(request, 'create_post.html')

@login_required(login_url='/login/')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You do not have permission to delete this post.")

    post.delete()
    return redirect('profile', username=request.user.username) 


@login_required(login_url='/login/')
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_text = request.POST.get('text', '')
        game_title = request.POST.get('game_title', '')
        post.image = request.FILES.get('image', post.image)
        post.video = request.FILES.get('video', post.video)

        if post_text.strip():
            post.text = post_text
            
            post.game_title = game_title.strip() if game_title.strip() else None
            
            post.save()
            
            return JsonResponse({
                'success': True,
                'post_id': post.id,
                'redirect_url': reverse('post_detail', args=[post.id])  # Redirect to the post detail page
            })
        
        else:
            return JsonResponse({'success': False, 'error': 'Post content cannot be empty'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def post_detail(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)  # Load the selected post
    user_profile = request.user.userprofile
    bookmarked_posts = [post.id for post in user_profile.bookmarks.all()]
    
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Handle the toggle like functionality
        user = request.user

        if selected_post.likes.filter(id=user.id).exists():
            selected_post.likes.remove(user)
            liked = False
        else:
            selected_post.likes.add(user)
            liked = True

        # Return the updated likes count as JSON
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': selected_post.likes.count()
        })

    # Default case: Render the post details
    likes_count = selected_post.likes.count()  # Count the number of likes on the post
    return render(request, 'home.html', {
        'selected_post': selected_post,
        'likes_count': likes_count,
        'post_id': selected_post.id,
        'bookmarked_posts': bookmarked_posts
    })

def fetch_new_posts(request):
    latest_posts = Post.objects.filter(timestamp__gte=timezone.now() - timezone.timedelta(minutes=5))
    posts_json = serializers.serialize('json', latest_posts)
    return JsonResponse(posts_json, safe=False)

@login_required(login_url='/login/')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    all_users = User.objects.exclude(id=request.user.id)  # Exclude self from following options

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')
        remove_avatar = request.POST.get('remove_avatar')
        following_ids = request.POST.getlist('following')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save() 

        
        user_profile.bio = bio

        if remove_avatar:
            user_profile.avatar.delete()  # Deletes the avatar file from storage
            user_profile.avatar = None  # Set the field to null/blank

        # Update avatar if provided
        if avatar:
            user_profile.avatar = avatar

        # Save the profile
        user_profile.save()

        # Redirect to the profile page after saving
        return redirect('profile', username=request.user.username)

    context = {
        'user_profile': user_profile,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'all_users': all_users,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/login/')
def toggle_like(request, post_id):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        return JsonResponse({
            "success": True,
            "liked": liked,
            "like_count": post.likes.count()
        })
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required(login_url='/login/')
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get("text")
        if not text:
            return JsonResponse({"error": "Content cannot be empty"}, status=400)

        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )

        # Return necessary data for dynamically updating the comment section
        return JsonResponse({
            "success": True,
            "text": comment.text,
            "user": f"{request.user.first_name} {request.user.last_name}",
            "username": request.user.username,
            "timestamp": localtime(comment.timestamp).strftime("%Y-%m-%d %H:%M"),
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_profile_recommendations(user, limit=3):
    # Get a list of user IDs that the current user is already following
    following_user_ids = Follower.objects.filter(user=user).values_list('followed_user_id', flat=True)

    # Get recommendations by excluding users the current user is following and the user themselves
    recommendations = UserProfile.objects.exclude(
        Q(user__id__in=following_user_ids) | Q(user=user)
    ).order_by('?')[:limit]

    return recommendations


@login_required(login_url='/login/')
def toggle_bookmark(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        user_profile = request.user.userprofile  # Fetch the user's profile
        bookmarked = False

        # Toggle the bookmark status
        if user_profile.bookmarks.filter(id=post.id).exists():  
            user_profile.bookmarks.remove(post)
        else:
            user_profile.bookmarks.add(post)
            bookmarked = True

        # Return the updated bookmark status
        return JsonResponse({'bookmarked': bookmarked})
    
    return HttpResponseBadRequest("Invalid request")
    

@login_required(login_url='/login/')
def view_bookmarks(request):
    user_profile = request.user.userprofile

    # Sort bookmarks by timestamp (descending order)
    sorted_bookmarks = sorted(
        user_profile.bookmark_timestamps.items(),
        key=lambda x: x[1],  # Sort by timestamp
        reverse=True
    )

    bookmarks = [Post.objects.get(id=post_id) for post_id, _ in sorted_bookmarks]
    bookmarked_posts = [post.id for post in user_profile.bookmarks.all()]

    return render(request, 'view_bookmarks.html', 
                  {'bookmarks': bookmarks, 
                   'bookmarked_posts': bookmarked_posts })

@login_required(login_url='/login/')
def global_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        limit = 10
        # Search profiles (username, bio)
        profiles = UserProfile.objects.filter(
            Q(user__username__icontains=query) | 
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(bio__icontains=query)
        ).select_related('user')[:limit]

        # Search posts (text content)
        posts = Post.objects.filter(
            Q(text__icontains=query)
        ).select_related('author')[:limit]

        game_zones = Post.objects.filter(
            Q(game_title__icontains=query)
        ).values_list('game_title', flat=True).distinct()[:limit]

        # Prepare results for JSON response
        profiles_data = [{
            'username': profile.user.username,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'bio': profile.bio,
            'avatar': profile.avatar.url if profile.avatar else None,
            'profile_url': f'/profile/{profile.user.username}/'
        } for profile in profiles]

        posts_data = [{
            'id': post.id,
            'text': post.text,
            'author': post.author.username,
            'post_url': f'/post/{post.id}/',
            'created_at': post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        } for post in posts]

        game_zones_data = [{
            'game_title': title,
            'game_url': f'/game_zone/{title}/'
        } for title in game_zones]

        return JsonResponse({'profiles': profiles_data, 
                             'posts': posts_data,
                             'game_zones': game_zones_data
                             },status=200)

    return JsonResponse({'error': 'No query provided'}, status=400)


def create_notification(user, sender, notification_type, post=None, comment=None):
    Notification.objects.create(
        user=user,
        sender=sender,
        notification_type=notification_type,
        post=post,
        comment=comment
    )

@login_required(login_url='/login/')
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    notifications.filter(is_read=False).update(is_read=True)

    post_related_notifications = ['like', 'comment', 'bookmark']

    return render(request, 'notifications.html', 
                  {'notifications': notifications,
                  'post_related_notifications' : post_related_notifications
                  })


@login_required(login_url='/login/')
def check_notifications(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).exists()
    return JsonResponse({'unread': unread})


@login_required(login_url='/login/') 
def game_zone_list(request):
    # Get distinct game titles from all posts
    game_titles = Post.objects.exclude(game_title__isnull=True).exclude(game_title='').values_list('game_title', flat=True).distinct()
    game_titles = [title.strip() for title in game_titles]
    
    game_list = [   
        (game, get_game_image(game))
        for game in game_titles
    ]

    game_images = {game[0].strip().lower(): game[1] for game in game_list}

    print("Game Titles:", game_titles)
    print("Game Images:", game_images)     

    return render(request, "game_zone_list.html",
        {"game_titles": game_titles,
         "game_images": game_images,
         "default_game_image": '/static/images/default_game_avatar.jpg'}
    )


def game_zone_ajax(request):
    # AJAX endpoint for dynamic search
    query = request.GET.get('q', '')
    if query:
        filtered_games = Post.objects.filter(Q(game_title__icontains=query)).values_list('game_title', flat=True).distinct()
    else:
        filtered_games = Post.objects.values_list('game_title', flat=True).distinct()

    return JsonResponse({'games': list(filtered_games)})


@login_required(login_url='/login/') 
def game_zone(request, game_title): 
    # Fetch posts filtered by the selected game_title
    posts = Post.objects.filter(game_title=game_title).order_by('-timestamp')

    user_profile = request.user.userprofile
    bookmarked_posts = [post.id for post in user_profile.bookmarks.all()]

    return render(request, 'game_zone.html', 
                  {'posts': posts, 
                   'game_title': game_title,
                   'bookmarked_posts': bookmarked_posts
                   })


def get_game_image(game_title):
    cache_key = f"game_image_{slugify(game_title)}"
    image_url = cache.get(cache_key)
    # RAWG_API_KEY = config('RAWG_API_KEY')

    if not image_url:
        # If not cached, fetch from RAWG API
        response = requests.get(f"https://api.rawg.io/api/games", params={
            'search': game_title,
            'key': 'RAWG_API_KEY'
        })
        if response.status_code == 200:
            data = response.json()
            # Check if there are results and that 'background_image' exists
            if data.get('results') and 'background_image' in data['results'][0]:
                image_url = data['results'][0]['background_image']
            else:
                # Fallback to default image if no valid image found
                image_url = '/static/images/default_game_avatar.jpg'
        else:
            # Fallback to default image
            image_url = '/static/images/default_game_avatar.jpg'
        
        # Cache the image URL for 1 day
        cache.set(cache_key, image_url, timeout=86400)

    return image_url