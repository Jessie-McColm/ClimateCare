from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        # can add email field if we wanted by adding it to this list like 'email'
        fields = ['username', 'password1','password2']
