from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from app.models import *


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']

class CreateEventForm(forms.ModelForm):


    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']  # Optional: Customize date format if needed
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']  # Optional: Customize date format if needed
    )
    class Meta:
        model = Events
        fields = ['name','description','event_image','event_location','address','start_datetime','end_datetime']
class AddMembersToEventForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Events.objects.none(), required=True)
    usernames = forms.CharField(required=True, help_text="Enter usernames separated by commas")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AddMembersToEventForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['event'].queryset = Events.objects.filter(user=user)

class CreateChatChannel(forms.Form):
    pass

class CreateUserForm(UserCreationForm):
    
    #Subclass for all the fields
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type a message...'}),


        }

class SelectEventForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Events.objects.none(), empty_label="Choose an Event", widget=forms.Select)
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'].queryset = Events.objects.filter(user=user)  # User-created events