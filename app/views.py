from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from app.forms import CreateUserForm
from django.contrib.auth.decorators import login_required


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


    