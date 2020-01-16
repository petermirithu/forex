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
   
