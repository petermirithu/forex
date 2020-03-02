from django.contrib.auth.models import User
from django import forms
from .models import *
from django.contrib.admin import widgets
from django.forms.fields import DateField



class LoginForm(forms.ModelForm):        
    class Meta:
      model=User
      fields=['username','password']

    
    
class BinaryForm(forms.ModelForm):
  
  class Meta:
    model = BinarySignals
    fields = [
      'currency_pair',
      'signal',
    ]
  
class ForexForm(forms.ModelForm):
  class Meta:
    model = ForexSignals
    exclude = [
      'posted_by',
      'posted_on',
    ]
   
class BlogForm(forms.ModelForm):
  class Meta:
    model = Blogs
    exclude = [
      'posted_by',
      'posted_on',
    ]
            
class UserUpdateform(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = [
            'username',
            'email',
        ]

class UpdateProfileForm(forms.ModelForm):
    bio = forms.Textarea()
    class Meta:
        model = Profile
        exclude =[
            'updated_on',
            'user',
            'user_app_id',
            'signup_confirmation',
        ]