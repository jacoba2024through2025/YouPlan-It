from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from app.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.models import *
from django.views import View



def viewHomePage(request):
    if request.user.is_authenticated:
        context = {
            'events': Events.events_within_next_14_days(request.user),
            'user': request.user,
            'profile': Profile.objects.get(user=request.user)
        }
    else:
        context = {
            'events': 0,
            'user': 0,
            'profile': None  
        }

    return render(request, 'base.html', context)
    

def viewLoginPage(request):
    if request.user.is_authenticated:
        print("You are already logged in")
        return redirect('home')
    else:
        print("You are not authenticated")

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Log the input for debugging purposes
        print(f"Attempting to authenticate with Username: {username} and Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Inform the user that the credentials were incorrect
            messages.error(request, "Username or Password is Incorrect")
            print("Authentication failed")

    # No need to pass context explicitly for messages as it's automatically handled
    return render(request, 'login.html')


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
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)  
    
    context = {
        'user': user,
        'events': Events.objects.filter(user=request.user),
        'profile': profile,
        'myevents': Events.objects.filter(user=request.user),
        'invites': user.pending.filter(invitepending=user)
    }

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
        'profile': profile,
        'events':Events.objects.filter(user=request.user)  # Pass profile to template for image display
    })
@login_required
def EventPage(request, username):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)  
        context = {
            'myevents': Events.objects.filter(user=request.user),
            'user': request.user,
            'profile': profile  
        }
    return render(request, 'eventform1.html', context)
def SharedEventPage(request, username):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)  
        context = {
            'myevents': Events.objects.filter(user=request.user),
            'events': Events.objects.filter(members=request.user).exclude(user=request.user),
            'user': request.user,
            'profile': profile  
        }
    return render(request, 'eventform2.html', context)
class EventCreateView(View):
    def get(self, request, username):
        form = CreateEventForm()
        return render(request, 'eventcreation.html', {'form': form, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user)})

    def post(self, request, username):
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # Assuming the user is logged in
            event.save()
            event.members.add(request.user)  # Add the creator to the members field
            return redirect('event_detail', username=event.user.username, ename=event.name)
        return render(request, 'eventcreation.html', {'form': form, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user)})
class EventUpdateView(View):
    def get(self, request, username, ename):
        update = Events.objects.get(name=ename, user=User.objects.get(username=username))
        form = CreateEventForm(instance=update)
        return render(request, 'eventcreation.html', {'form': form, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user)})

    def post(self, request, username, ename):
        update = Events.objects.get(name=ename, user=User.objects.get(username=username))
        form = CreateEventForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # Assuming the user is logged in
            event.save()
            event.members.add(request.user)  # Add the creator to the members field
            return redirect('event_detail', username=event.user.username, ename=event.name)
        return render(request, 'eventcreation.html', {'form': form, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user)})
    
def EventDetail(request, username, ename):
    event = Events.objects.get(name=ename, user=User.objects.get(username=username))
    members = event.members.all()
    return render(request, 'eventdetails.html', {'event': event, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user), 'members':members.exclude(username=event.user)})

def InviteUser(request, username):
    if request.method == 'POST':
        form = AddMembersToEventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.cleaned_data['event']
            usernames = form.cleaned_data['usernames']
            username_list = [username.strip() for username in usernames.split(',')]
            members = []
            invalid_usernames = []
            for username in username_list:
                try:
                    user = User.objects.get(username=username)
                    members.append(user)
                except User.DoesNotExist:
                    invalid_usernames.append(username)
            
            if invalid_usernames:
                success = f"Unable to find users: {', '.join(invalid_usernames)}."
            else:
                event.invitepending.add(*members)
                success = "User(s) invited successfully."
            invited_profiles = []
            for member in members:
                profile = Profile.objects.get(user=member)
                invited_profiles.append(profile)
            
            context = {'form': form,
                'myevents': Events.objects.filter(user=request.user),
               'success': success,
               'profile': Profile.objects.get(user=request.user),
               'invited_profiles': invited_profiles,
               }
            return render(request, 'invites.html', context)
    else:
        form = AddMembersToEventForm(user=request.user)
    success = ""
    context = {'form': form,
               'myevents': Events.objects.filter(user=request.user),
               'success': success,
               'profile': Profile.objects.get(user=request.user)}
    return render(request, 'invites.html', context)

@login_required

@login_required
def ChatRoom(request, username):
    context = {
        'profile': Profile.objects.get(user=request.user),
        'myevents': Events.objects.filter(user=request.user)
    }
    return render(request, 'chatroom.html', context)

def deleteEvent(request, username, ename):
    event = Events.objects.get(name=ename, user=User.objects.get(username=username))
    event.delete()
    return redirect('event_page', username=username)
def acceptInvite(request, username, ename):
    event = Events.objects.get(name=ename, user=User.objects.get(username=username))
    event.members.add(request.user)
    event.invitepending.remove(request.user)
    return redirect('user_dashboard', username=request.user.username)
def declineInvite(request, username, ename):
    event = Events.objects.get(name=ename, user=User.objects.get(username=username))
    event.invitepending.remove(request.user)
    return redirect('user_dashboard', username=request.user.username)