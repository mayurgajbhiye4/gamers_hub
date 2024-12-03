from django.shortcuts import render,  redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.core import serializers
from django.utils.timezone import localtime
from django.urls import reverse


@login_required(login_url='/login/')
def home(request):
    posts = list(Post.objects.all().order_by('-timestamp'))
    recommendations = get_profile_recommendations(request.user)
    return render(request, 'home.html', 
                  {'posts': posts, 
                   'recommendations': recommendations,
                   'user_likes': {post.id: post.likes.count() for post in posts}
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

@login_required
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

@login_required 
def followers(request, username):   
    user  = get_object_or_404(User, username=username) 
    profile_owner  = get_object_or_404(UserProfile, user=user)
    followers = Follower.objects.filter(followed_user=user)  

    followers_profiles = [f.user for f in followers]    

    return render(request, 'followers.html', {'profile_owner':profile_owner, 'followers': followers_profiles})


@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    current_user = request.user

    if current_user == target_user:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself'}, status=400)

    # Check if the relationship exists
    follow, created = Follower.objects.get_or_create(user=current_user, followed_user=target_user)

    if not created:
        # If it already exists, remove it (unfollow)
        follow.delete()
        return JsonResponse({'success': True, 'following': False})

    return JsonResponse({'success': True, 'following': True})


def profile(request, username):
    # Fetch the user profile based on the provided username
    profile_owner  = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get(user=profile_owner)

    # Fetch the user's posts, ordered by the latest first
    posts = Post.objects.filter(author=profile_owner).order_by('-timestamp')

    # Check if the logged-in user is viewing their own profile
    is_own_profile = request.user == profile_owner

    recommendations = get_profile_recommendations(request.user)
    # Context to pass to the template
    context = {
        'profile_owner': profile_owner,
        'user_profile': user_profile,
        'first_name': profile_owner.first_name,
        'last_name': profile_owner.last_name,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'recommendations': recommendations
    }

    return render(request, 'profile.html', context)

def validate_file_size(file, max_size):
    if file.size > max_size:
        raise ValidationError(f"File size exceeds {max_size / (1024 * 1024)} MB")


@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
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
            image=image,
            video=video
        )
        post.save()
        return redirect('home')  # Redirect to the homepage or another page

    return render(request, 'create_post.html')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You do not have permission to delete this post.")

    post.delete()
    return redirect('profile', username=request.user.username) 


@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_text = request.POST.get('text', '')
        post.image = request.FILES.get('image', post.image)
        post.video = request.FILES.get('video', post.video)

        if post_text.strip():
            post.text = post_text
            post.save()
            
            return JsonResponse({
                'success': True,
                'post_id': post.id,
                'redirect_url': reverse('post_detail', args=[post.id])  # Redirect to the post detail page
            })
        
        else:
            return JsonResponse({'success': False, 'error': 'Post content cannot be empty'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def post_detail(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)  # Load the selected post

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
            'likes_count': selected_post.likes.count(),
        })

    # Default case: Render the post details
    likes_count = selected_post.likes.count()  # Count the number of likes on the post
    return render(request, 'home.html', {
        'selected_post': selected_post,
        'likes_count': likes_count,
        'post_id': post_id,
    })

def fetch_new_posts(request):
    latest_posts = Post.objects.filter(timestamp__gte=timezone.now() - timezone.timedelta(minutes=5))
    posts_json = serializers.serialize('json', latest_posts)
    return JsonResponse(posts_json, safe=False)

@login_required 
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    all_users = User.objects.exclude(id=request.user.id)  # Exclude self from following options

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')
        following_ids = request.POST.getlist('following')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        # Update bio
        if bio:
            user_profile.bio = bio

        # Update avatar if provided
        if avatar:
            user_profile.avatar = avatar

        # Update following list
        user_profile.following.set(following_ids)  # Set the selected users as following

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


@login_required
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


@login_required
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

  
@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.views_count = models.F('views_count') + 1  # Increment views
    post.save(update_fields=['views_count'])
    return redirect('post_detail', post_id=post_id)


def get_profile_recommendations(user, limit=3):
    # Get a list of user IDs that the current user is already following
    following_user_ids = Follower.objects.filter(user=user).values_list('followed_user_id', flat=True)

    # Get recommendations by excluding users the current user is following and the user themselves
    recommendations = UserProfile.objects.exclude(
        Q(user__id__in=following_user_ids) | Q(user=user)
    ).order_by('?')[:limit]

    return recommendations


@login_required
def bookmark_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        user_profile = request.user.userprofile
        bookmarked = False

        # Toggle bookmark
        if post in user_profile.bookmarks.all():
            user_profile.bookmarks.remove(post)
        else:
            user_profile.bookmarks.add(post)
            bookmarked = True

        # Return JSON response for AJAX
        return JsonResponse({'bookmarked': bookmarked})
    
    return HttpResponseBadRequest("Invalid request")
    

@login_required
def view_bookmarks(request):
    profile = request.user.userprofile
    bookmarks = profile.bookmarks.all()  # Fetch all bookmarked posts

    return render(request, 'view_bookmarks.html', {'bookmarks': bookmarks})


@login_required
def unbookmark_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            request.user.userprofile.bookmarks.remove(post)
            return JsonResponse({'status': 'success'})
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def global_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        # Search profiles (username, bio)
        profiles = UserProfile.objects.filter(
            Q(user__username__icontains=query) | Q(bio__icontains=query)
        ).select_related('user')

        # Search posts (text content)
        posts = Post.objects.filter(
            Q(text__icontains=query)
        ).select_related('author')

        # Prepare results for JSON response
        profiles_data = [{
            'username': profile.user.username,
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

        return JsonResponse({'profiles': profiles_data, 'posts': posts_data}, status=200)

    return JsonResponse({'error': 'No query provided'}, status=400)


