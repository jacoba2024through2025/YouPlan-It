from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import Group, Permission


##model for event creation
class Events(models.Model):
    ##The name of the event -- This field is required by default
    name = models.CharField(max_length=200)
    
    ##The event's description
    description = models.CharField(max_length=500)
    ##The user can provide an image if they want to
    event_image = models.ImageField(upload_to='event_images', blank=True, null=True)


    ##The user that is associated with the event (should be the one currently logged in)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

    #for the invited users for an event
    members = models.ManyToManyField(User, related_name='invitedusers')
    invitepending = models.ManyToManyField(User, related_name='pending')
    ###Fields for the dates of when the event starts and when it ends
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    ##allows the user to give the event a location if they desire
    event_location = models.CharField(max_length=300, blank=True, null=True)
    ##allows the user to specify an address for the event
    address = models.CharField(max_length=500, blank=True, null=True)

    
    


    ##returns the name of the event for testing purpose's in the admin page

    def __str__(self):
        return self.name
    
    def events_within_next_14_days(who):
        now = timezone.now()
        next_14_days = now + timedelta(days=14)
        return who.invitedusers.filter(start_datetime__gte=now, start_datetime__lte=next_14_days, members=who).order_by('start_datetime')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.user.username} at {self.timestamp}'