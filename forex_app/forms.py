from django.contrib.auth.models import User
from django import forms
from .models import Forex


class LoginForm(forms.ModelForm):        
    class Meta:
      model=User
      fields=['username','password']
   