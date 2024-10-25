from django.shortcuts import render,  redirect
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment
from .forms import signupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
