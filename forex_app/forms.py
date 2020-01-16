from django.contrib.auth.models import User
from django import forms
from .models import *


class LoginForm(forms.ModelForm):        
    class Meta:
      model=User
      fields=['username','password']

    # def clean(self,*args,**kwargs):
    #     email = self.cleaned_data.get('email')
    #     password = self.cleaned_data.get('password')

    #     if email and password:
    #         user = User.objects.get(email = email,password = password)
    #         if not user:
    #             raise forms.ValidationError('user doesnot exist')
    #         if not user.check_password(password):
    #             raise forms.ValidationError('incorrect password')
    #     return super(LoginForm,self).clean(*args, **kwargs)
    
    
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