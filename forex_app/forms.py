from django.contrib.auth.models import User
from django import forms
from .models import *


class LoginForm(forms.ModelForm):        
    class Meta:
      model=User
      fields=['username','password']

    
    
class BinaryForm(forms.ModelForm):
  class Meta:
    model = BinarySignals
    exclude = [
      'posted_by',
      'posted_on',
    ]
  
class ForexForm(forms.ModelForm):
  class Meta:
    model = ForexSignals
    exclude = [
      'posted_by',
      'posted_on',
    ]
   
