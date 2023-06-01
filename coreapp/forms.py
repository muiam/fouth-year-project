from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Campaign

class CreateUserForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('investor', 'investor'),
        ('fund seeker', 'fundseeker'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=False)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'user_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Perform email cleaning/validation here
        # ...
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Perform first name cleaning/validation here
        # ...
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Perform last name cleaning/validation here
        # ...
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        # Perform additional cleaning/validation on the form data as a whole
        # ...
        return cleaned_data

class CreateProjectForm(ModelForm):
    class Meta:
        model=Campaign
        exclude=('owner','contributors','period')
            

    