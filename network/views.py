from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, FriendRequest, User
from django.core.exceptions import ValidationError

@login_required(login_url='/login/')
def home(request):
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, 'home.html', {'posts': posts})

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
def following(request):
    user_profile = request.user.userprofile

    # Get all users the current user is following
    following = user_profile.following.all()

    # Get all users following the current user
    followers = user_profile.followers.all()

    return render(request, 'following.html', {
        'following': following,
        'followers': followers
    })

@login_required
def follow_user(request, user_id):
    to_follow = get_object_or_404(User, id=user_id)
    request.user.userprofile.following.add(to_follow.userprofile)  # Add to following list
    return redirect('profile', user_id=user_id)  # Redirect to the user's profile

@login_required
def unfollow_user(request, user_id):
    to_unfollow = get_object_or_404(User, id=user_id)
    request.user.userprofile.following.remove(to_unfollow.userprofile)  # Remove from following list
    return redirect('profile', user_id=user_id)  # Redirect to the user's profile


def profile(request, username):
    # Fetch the user profile based on the provided username
    user = get_object_or_404(User, username=username)

    # Fetch the user's posts, ordered by the latest first
    posts = Post.objects.filter(author=user).order_by('-timestamp')

    # Check if the logged-in user is viewing their own profile
    is_own_profile = request.user == user

    # Context to pass to the template
    context = {
        'profile_user': user,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'posts': posts,
        'is_own_profile': is_own_profile,
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