from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

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
    user_profile = get_object_or_404(UserProfile, user=request.user)
    following = user_profile.friends.all()
    return render(request, 'following.html', {'following': following})