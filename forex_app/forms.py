from django.contrib.auth import get_user_model
from django import forms

# `User = get_user_model()
# class LoginForm(forms.Form):
#     email = forms.EmailField(label='Email')
#     password = forms.CharField(widget=forms.PasswordInput)

#     def clean(self,*args,**kwargs):
#         email = self.cleaned_data.get('email')
#         password = self.cleaned_data.get('password')

#         if email and password:
#             user = User.objects.filter(email = email,password = password)
#             if not user:
#                 raise forms.ValidationError('user doesnot exist')
#             if not user.check_password(password):
#                 raise forms.ValidationError('incorrect password')
#         return super(LoginForm,self).clean(*args, **kwargs)`