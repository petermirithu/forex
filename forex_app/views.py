from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text,force_bytes
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string
from .email import send_register_confirm_email

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name =request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password1 =request.POST['password1']

        if password1 == password:
            if User.objects.filter(username = username):
                messages.info(request,'This username is taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username = username,password = password,email = email,first_name = first_name,last_name = last_name,)
                user.is_active=False
                user.save()

                forex_site=get_current_site(request)
                domain=forex_site.domain
                uid=urlsafe_base64_encode(force_bytes(user.pk))
                token=account_activation_token.make_token(user)                    
                send_register_confirm_email(username,email,domain,uid,token)                                
                return redirect('activation_sent')                
        else:
            messages.info(request,'passwords should match')
            return redirect('register')
        
    else:        
        return render(request,'authentication/registration.html')

def activation_sent(request):
    return render(request, 'authentication/activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=pk)
    except (TypeError, ValueError ,OverflowError, User.DoesNotExist):
        user=None

    if user is not None and account_activation_token.check_token(user, token):        
        user.is_active=True
        user.profile.signup_confirmation =True
        user.save()
        login(request,User)
        return redirect('home')
    else:
        return render(request, 'authentication/activation_invalid.html')    

        # end of authentication
@login_required(login_url = 'register_account/')
def home(request):
    return render(request,'index.html')


