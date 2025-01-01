from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from app.forms import CreateUserForm, ProfileImageForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.models import *



def viewHomePage(request):
    


    return render(request, 'base.html')


def viewLoginPage(request):
    
    if request.user.is_authenticated:

        print("You are already logged in")
        return redirect('home')
    else:
        print("You are not authenticated")

    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        print(user.username)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username or Password is Incorrect")

    context = {}
    return render(request, 'login.html', context)


def viewRegistrationPage(request):
    
    if request.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')  

    context = {'form': form}
    return render(request, 'register.html', context)

def viewLogout(request):
    logout(request)
    return redirect('login')



@login_required
def viewUserDashboard(request, username):
    ##grabs the User model and all of its objects
    user = get_object_or_404(User, username=username)

    ##if it cant find the User object, it will return a 404 error


    
    context = {"user": user}


    return render(request, 'userdashboard.html', context)

def viewUserProfile(request, username):

    # Get the user object, or return a 404 if not found
    user = get_object_or_404(User, username=username)

    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=user)

    # Handle form submission (POST)
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()  # Save the profile with the new data
            return redirect('profile', username=username)  # Redirect after saving
    else:
        # Initialize the form with the current profile data (GET)
        form = ProfileImageForm(instance=profile)

    # Pass the user and profile to the template context
    return render(request, 'profile.html', {
        'form': form,
        'user': user,
        'profile': profile,  # Pass profile to template for image display
    })