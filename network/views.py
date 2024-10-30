from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, FriendRequest, User

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