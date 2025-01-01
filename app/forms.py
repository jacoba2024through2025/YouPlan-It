from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from app.models import *


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']

class CreateUserForm(UserCreationForm):
    
    #Subclass for all the fields
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']