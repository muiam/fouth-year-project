from django.forms import ModelForm
from .models import Contributions
from django import forms

class ContributionForm(forms.Form):
    amount=forms.CharField(max_length=20)
