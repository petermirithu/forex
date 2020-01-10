from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model,login,authenticate,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text,force_bytes
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .tokens import account_activation_token
from .email import send_register_confirm_email
from .models import profile,Forex
from .forms import LoginForm,FreeForexForm,SilverForexForm
from django.contrib.auth.hashers import check_password


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
                messages.info(request,'This Username is taken!')
                return redirect('register')
            elif User.objects.filter(email=email):
                messages.info(request,'This Email is taken!')
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
            messages.info(request,'passwords should match!')
            return redirect('register')
        
    else: 
        return render(request,'authentication/registration.html')

def activation_sent(request):
    return render(request, 'authentication/activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except (TypeError, ValueError ,OverflowError, User.DoesNotExist):
        user=None

    if user is not None and account_activation_token.check_token(user, token):        
        user.is_active=True
        user.profile.signup_confirmation =True
        user.save()
        login(request,user)
        return redirect('home')
    else:
        return render(request, 'authentication/activation_invalid.html')    

def login_user(request):
    if request.method=='POST':        
        form=LoginForm(request.POST)        
        user_name=request.POST.get('username')
        passwd=request.POST.get('password')
        if user_name and passwd:
            try:
                user_x=User.objects.get(username=user_name)                
                matched=check_password( passwd, user_x.password)
                user_profile=profile.get_user_profile(user_x.id)                   
                if  matched==False:        
                    messages.info(request,'Password is invalid!')
                    return redirect('login')        

                elif user_profile.signup_confirmation==False:
                    messages.info(request,'Activation invalid. Please check your email to activate your account!')
                    return redirect('login')
                else:    
                    login(request,user_x)
                    return redirect('home')
                
            except User.DoesNotExist:                
                messages.info(request,'That username doesnot exist!')
                return redirect('login')                              
        else:
            messages.info(request,'All fields are required!')
            return redirect('login')

    else:
        title="Login"
        form=LoginForm()
        context={
            'title':title,
            'form':form,
        }
        return render(request, 'authentication/login.html',context)  

@login_required(login_url="/login_account/")
def logout_request(request):  
  logout(request)
  return redirect('home')

# end of authentication...................................................................................
@login_required(login_url="/login_account/")
def home(request):
    return render(request,'index.html')

@login_required(login_url="/login_account/")
def forex_account_type(request,acc_type):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email = email)
            if user.email != request.user.email:
                messages.info(request,'please use your correct email address that you registered with.')
                return redirect('select_account')
            else:
                id_forex = random.randint(0000000,9999999)
                user_profile = profile.objects.get(user = user)
                user_profile.user_app_id = id_forex
                user_profile.save()
                
                user_forex = Forex(user = request.user,account_type = acc_type,payment = 0)
                user_forex.save()
                return redirect('home')
        except User.DoesNotExist:
            messages.info(request,'please enter a valid email')
            return redirect('select_account')
       
    