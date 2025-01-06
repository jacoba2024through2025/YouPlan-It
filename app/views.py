from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from app.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.models import *
from django.views import View
from django.contrib.auth.models import Group, Permission


def viewHomePage(request):
    if request.user.is_authenticated:
        context = {
            'events': Events.events_within_next_14_days(request.user),
            'user': request.user,
            'profile': Profile.objects.get(user=request.user),
            
        }
    else:
        context = {
            'events': Events.objects.none(),  
            'user': None,
            'profile': None, 
            
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

        
        print(f"Attempting to authenticate with Username: {username} and Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            
            messages.error(request, "Username or Password is Incorrect")
            print("Authentication failed")

    
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
    shared_events = Events.objects.filter(members=request.user).exclude(user=request.user)
    context = {
        'user': user,
        'events': Events.objects.filter(user=request.user),
        'profile': profile,
        'myevents': Events.objects.filter(user=request.user),
        'invites': user.pending.filter(invitepending=user),
        'shared_events': shared_events
    }

    return render(request, 'userdashboard.html', context)

def viewUserProfile(request, username):

    # Get the user object, or return a 404 if not found
    user = get_object_or_404(User, username=username)

    
    profile, created = Profile.objects.get_or_create(user=user)

    
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()  
            return redirect('profile', username=username)  
    else:
        
        form = ProfileImageForm(instance=profile)

    
    return render(request, 'profile.html', {
        'form': form,
        'user': user,
        'profile': profile,
        'events':Events.objects.filter(user=request.user)  
    })
@login_required
def EventPage(request, username):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        shared_events = Events.objects.filter(members=request.user).exclude(user=request.user)  
        context = {
            'myevents': Events.objects.filter(user=request.user),
            'user': request.user,
            'profile': profile,
            'shared_events': shared_events  
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
        return render(request, 'eventcreation.html', {
            'form': form, 
            'myevents': Events.objects.filter(user=request.user),
            'profile': Profile.objects.get(user=request.user)
        })

    def post(self, request, username):
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            
            event = form.save(commit=False)
            event.user = request.user  
            event.save()

            

            event.members.add(request.user)  
            return redirect('event_detail', username=request.user.username, ename=event.name)
        
        return render(request, 'eventcreation.html', {
            'form': form, 
            'myevents': Events.objects.filter(user=request.user),
            'profile': Profile.objects.get(user=request.user)
        })

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
            event.user = request.user  
            event.save()
            event.members.add(request.user)  
            return redirect('event_detail', username=event.user.username, ename=event.name)
        return render(request, 'eventcreation.html', {'form': form, 'myevents': Events.objects.filter(user=request.user), 'profile': Profile.objects.get(user=request.user)})
    
def EventDetail(request, username, ename):
    
    event = get_object_or_404(Events, name=ename, user__username=username)
    
    
    members = event.members.all().exclude(username=event.user.username)
    
    
    return render(request, 'eventdetails.html', {
        'event': event,
        'myevents': Events.objects.filter(user=request.user),
        'profile': Profile.objects.get(user=request.user),
        'members': members,
        'username': username,  
    })

def InviteUser(request, username):
    shared_events = Events.objects.filter(members=request.user).exclude(user=request.user)
    
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
            
            context = {
                'form': form,
                'myevents': Events.objects.filter(user=request.user),
                'success': success,
                'profile': Profile.objects.get(user=request.user),
                'invited_profiles': invited_profiles,
                'shared_events': shared_events
            }
            return render(request, 'invites.html', context)  # Check for tuple-like behavior
    else:
        form = AddMembersToEventForm(user=request.user)
    
    success = ""
    context = {
        'form': form,
        'myevents': Events.objects.filter(user=request.user),
        'success': success,
        'profile': Profile.objects.get(user=request.user),
        'shared_events': shared_events
    }
    
    return render(request, 'invites.html', context)  


@login_required


@login_required
def chat_room(request, username, event_id):
    # Get the event object using the event_id
    event = get_object_or_404(Events, id=event_id)
    
    shared_events = Events.objects.filter(members=request.user).exclude(user=request.user)

    # Check if the user is the event creator or a member (including those who have accepted invites)
    if request.user != event.user and request.user not in event.members.all():
        # If not a member, redirect to the event selection page to create a chat room
        return redirect('create_chat_room', username=username)

    # Handle the message submission in the chat room
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            # Save the message to the database
            ChatMessage.objects.create(event=event, user=request.user, message=message)

    # Get the messages for this event, ordered by timestamp (newest first)
    messages = ChatMessage.objects.filter(event=event).order_by('-timestamp')

    # Render the chat room template with the event and messages
    return render(request, 'chatroom.html', {
        'event': event,
        'messages': messages,
        'username': username,
        'profile': Profile.objects.get(user=request.user),
        'myevents': Events.objects.filter(user=request.user),  # User's events for the sidebar or navigation
        'shared_events': shared_events
    })





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

@login_required
def remove_member(request, username, ename):
    
    event = get_object_or_404(Events, name=ename, user__username=username)

    if request.method == 'POST':
        
        user_to_remove_username = request.POST.get('user_to_remove')
        user_to_remove = get_object_or_404(User, username=user_to_remove_username)

        
        event.members.remove(user_to_remove)

        
        return redirect('event_detail', username=username, ename=ename)
    


    
    return redirect('event_detail', username=username, ename=ename)







@login_required
def create_chat_room(request, username):
    if request.method == 'POST':
        form = SelectEventForm(request.user, request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            return redirect('chat_room', username=username, event_id=event.id)  
    else:
        form = SelectEventForm(request.user)

    return render(request, 'select_event.html', {
        'form': form,
        'username': username,
    })


