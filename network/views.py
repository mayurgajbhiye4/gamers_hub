from django.shortcuts import render,  redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
import random

@login_required(login_url='/login/')
def home(request):
    posts = list(Post.objects.all())
    random.shuffle(posts)
    recommendations = get_profile_recommendations(request.user)

    return render(request, 'home.html', {'posts': posts,  'recommendations': recommendations})

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
    user = get_object_or_404(User, username=username)
    following = user.following_set.all()  # All users this user is following
    return render(request, 'following.html', {'user': user, 'following': following})

@login_required 
def followers(request, username):   
    user  = get_object_or_404(User, username=username) 
    profile_owner  = get_object_or_404(UserProfile, user=user)
    followers = Follower.objects.filter(followed_user=user)  

    followers_profiles = [f.user for f in followers]

    return render(request, 'followers.html', {'profile_owner':profile_owner, 'followers': followers_profiles})


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    Following.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Following.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('profile', username=username)


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
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Toggle like
    return JsonResponse({'likes_count': post.likes.count()})

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('text')
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        return redirect('post_detail', post_id=post_id)
    
@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.views_count = models.F('views_count') + 1  # Increment views
    post.save(update_fields=['views_count'])
    return redirect('post_detail', post_id=post_id)


def get_profile_recommendations(user, limit=3):
   
    # Get the user's UserProfile instance   
    user_profile = user.userprofile

    # Exclude the profiles the user is already following and the user's own profile
    recommendations = UserProfile.objects.exclude(Q(followers=user_profile) | Q(user=user)
    ).order_by('?')[:limit]

    return recommendations


@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_profile = request.user.userprofile
    bookmarked = False

    # Toggle bookmark
    if post in user_profile.bookmarks.all():
        user_profile.bookmarks.remove(post)
    else:
        user_profile.bookmarks.add(post)
        bookmarked = True

    # Check if the request is AJAX; if so, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({'bookmarked': bookmarked})
    
    # Fallback in case it's not an AJAX request
    return HttpResponseRedirect(reverse('post_detail', args=[post_id]))


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


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the post is already bookmarked by the user
    is_bookmarked = post in request.user.userprofile.bookmarks.all()

    return render(request, 'post_detail.html', {
        'post': post,
        'is_bookmarked': is_bookmarked,
    })
