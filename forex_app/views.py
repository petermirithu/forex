from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text, force_bytes
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .tokens import account_activation_token
from .email import send_register_confirm_email
from .models import Profile,Forex,binary_accounts,Account_price,ForexSignals,BinarySignals
from .forms import *
from django.contrib.auth.hashers import check_password
import random
from django.conf import settings
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from paypal.standard.ipn.models import PayPalIPN
from django.contrib.auth.decorators import permission_required
import datetime as dt
from datetime import date
from datetime import datetime
import datetime



def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']

        if password1 == password:
            if User.objects.filter(username=username):
                messages.info(request, 'This Username is taken!')
                return redirect('register')
            elif User.objects.filter(email=email):
                messages.info(request, 'This Email is taken!')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email, first_name=first_name, last_name=last_name,)
                user.is_active = False
                user.save()

                domain = 'https://forex254.herokuapp.com'
               
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                send_register_confirm_email(
                    username, email,domain, uid, token)
                return redirect('activation_sent')
        else:
            messages.info(request, 'passwords should match!')
            return redirect('register')

    else:
        return render(request, 'authentication/registration.html')


def activation_sent(request):
    return render(request, 'authentication/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'authentication/activation_invalid.html')


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        user_name = request.POST.get('username')
        passwd = request.POST.get('password')
        if user_name and passwd:
            try:
                user_x = User.objects.get(username=user_name)
                matched = check_password(passwd, user_x.password)
                user_profile = Profile.get_user_profile(user_x.id)
                if matched == False:
                    messages.info(request, 'Password is invalid!')
                    return redirect('login')

                elif user_profile.signup_confirmation == False:
                    messages.info(
                        request, 'Activation invalid. Please check your email to activate your account!')
                    return redirect('login')
                else:
                    login(request, user_x)
                    return redirect('home')

            except User.DoesNotExist:
                messages.info(request, 'That username doesnot exist!')
                return redirect('login')
        else:
            messages.info(request, 'All fields are required!')
            return redirect('login')

    else:
        title = "Login"
        form = LoginForm()
        context = {
            'title': title,
            'form': form,
        }
        return render(request, 'authentication/login.html', context)


@login_required(login_url="/login_account/")
def logout_request(request):
    logout(request)
    return redirect('home')

# end of authentication...................................................................................

@login_required(login_url="/login_account/")
#------------------------------------------------------
def home(request):
    try:
        account_user = Forex.objects.get(user=request.user)
        date_today = dt.date.today()
        paid_on = account_user.paid_on.date()
        date_diff = date_today - paid_on
        subscription_rate = dt.timedelta(days =90 )
        if date_diff<=subscription_rate:
            if account_user.paid_confirmation==True :
                messages.info(request, f'Good to see you in {account_user.account_type} forex account!')
                return render(request, 'index.html')
            else:
                request.session['order_id']="Forex"
                messages.info(request, 'Please Pay to activate your account.')
                return redirect('process_payment')
        else:
            account_user.paid_confirmation = False
            account_user.save()
            request.session['order_id']="Forex"
            messages.info(request, 'Your subscription is over.Please pay pay for another package')
            return redirect('process_payment')

    except Forex.DoesNotExist:
        try:
            account_user = binary_accounts.objects.get(user=request.user)
            today = dt.date.today()
            paid_on = account_user.paid_on.date()
            
            diff_date = today - paid_on
            subscription_rate = dt.timedelta(days =90 )
            
            if diff_date <= subscription_rate:
                if account_user.paid_confirmation==True:
                    messages.info(
                        request, f'Good to see you in {account_user.account_type} binary account!')
                    return render(request, 'index.html')
                else:                
                    request.session['order_id']="Binary"
                    messages.info(request, 'Please Pay to activate your account.')
                    return redirect('process_payment')                
            else:
                account_user.paid_confirmation = False
                account_user.save()
                request.session['order_id']="Binary"
                messages.info(request, 'Your subscription is over.Please pay pay for another package')
                return redirect('process_payment')                
            
        except binary_accounts.DoesNotExist:
            return redirect('select_account')

#------------------------------------------------

# selecting account
@login_required(login_url="/login_account/")
def select_account(request):
    title = 'Select account'
    context = {
        'title': title,
    }
    return render(request, 'select_acc.html', context)
@login_required(login_url="/login_account/")
def forex_account_type(request, acc_type):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.email != request.user.email:
                messages.info(
                    request, 'please use your correct email address that you registered with.')
                return redirect('select_account')
            else:
                if acc_type=='free':    
                    id_forex = random.randint(0000000, 9999999)
                    user_profile = Profile.objects.get(user=user)
                    user_profile.user_app_id = id_forex
                    user_profile.save()

                    user_forex = Forex(user=request.user,account_type=acc_type, payment=0,paid_confirmation=True)
                    user_forex.save()
                    return redirect('home')
                else:
                    user_x=Forex(user=request.user,account_type=acc_type,payment=10)
                    user_x.save()

                    request.session['order_id'] = acc_type
                    return redirect('process_payment')
                
        except User.DoesNotExist:
            messages.info(request, 'please enter a valid email')
            return redirect('select_account')


def binary_account_type(request, acc_type):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user_exists = User.objects.get(email=email)
            if user_exists.email != request.user.email:
                messages.info(
                    request, 'Please use your correct email address that you registered with!')
                return redirect('select_account')
            else:
                if acc_type=="free":                    
                    id_gen = random.randint(0000000, 9999999)
                    user_profile = Profile.objects.get(user=user_exists)
                    user_profile.user_app_id = id_gen
                    user_profile.save()

                    user_binary_acc = binary_accounts(user=request.user, account_type=acc_type, payment=0,paid_confirmation=True)
                    user_binary_acc.save()
                    return redirect('home')
                else:

                    user_x=binary_accounts(user=request.user,account_type=acc_type,payment=10)    
                    user_x.save()

                    request.session['order_id'] = acc_type
                    return redirect('process_payment')

        except User.DoesNotExist:
            messages.info(request, 'Please enter a valid email!')
            return redirect('select_account')

# selecting account over

# paypal  process
def process_payment(request):
  
    order_id = request.session.get('order_id')
    if order_id=='forexsilver':
        vari_x='Forex'        
        account_type = get_object_or_404(Account_price, account_type=vari_x)
        paypal_dict = {

            'business': settings.PAYPAL_RECEIVER_EMAIL,

            'amount': '%.2f' % account_type.price,

            'item_name': '{}'.format(account_type.account_type),

            'invoice': str(random.randint(00000,99999)),

            'currency_code': 'USD',
            
            'notify_url': 'https://forex254.herokuapp.com/q-forex-binary-f-k-defw-dshsgdtdhvdsss-scczzc-url/',

            'return_url': 'https://forex254.herokuapp.com/payment-done/',

            'cancel_return': 'https://forex254.herokuapp.com/payment-cancelled/',
        }
        
        form = PayPalPaymentsForm(initial=paypal_dict)


        return render(request, 'paypal/process_payment.html', {'account_type': account_type, 'form': form})
    
    else:
        vari_y='Binary'
        account_type = get_object_or_404(Account_price, account_type=vari_y)        
        paypal_dict = {

            'business': settings.PAYPAL_RECEIVER_EMAIL,

            'amount': '%.2f' % account_type.price,

            'item_name': '{}'.format(account_type.account_type),

            'invoice': str(random.randint(00000,99999)),

            'currency_code': 'USD',
            
            'notify_url': 'https://forex254.herokuapp.com/q-forex-binary-f-k-defw-dshsgdtdhvdsss-scczzc-url/',

            'return_url': 'https://forex254.herokuapp.com/payment-done/',

            'cancel_return': 'https://forex254.herokuapp.com/payment-cancelled/',
        }

        form = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'paypal/process_payment.html', {'account_type': account_type, 'form': form})
    
@csrf_exempt
def payment_done(request):    

    try:
        user_x=Forex.objects.get(user=request.user)   
        user_x.paid_confirmation=True
        user_x.paid_now = dt.date.today()
        user_x.save()
        messages.info(request, 'Welcome to your Forex Account!')
        return render(request, 'paypal/payment_done.html')

    except Forex.DoesNotExist:

        try:
            user_y=binary_accounts.objects.get(user=request.user)    
            user_y.paid_confirmation=True
            user_y.paid_now = dt.date.today()
            user_y.save()
            messages.info(request, 'Welcome to your Binary Account!')
            return render(request, 'paypal/payment_done.html')

        except binary_accounts.DoesNotExist:
            messages.info(request, 'Invalid action!')
            return render(request, 'paypal/payment_error.html')                                               
 
@csrf_exempt
def payment_canceled(request):    
    return render(request, 'paypal/payment_cancelled.html')

#END OF PAYPAL PROCESS

# ADMIN
#binaryform
@login_required(login_url="/login_account/")
@permission_required("True", "home")
def binaryform(request):
    if request.method == 'POST':
        form = BinaryForm(request.POST)
        expe=str(request.POST.get('input_time'))
        list1=expe.split(' ')
        time=list1[0].split(':')
        date=list1[1].split('/')
        print(date)
        final="{}-{}-{} {}:{}".format(date[-1],date[-3],date[-2],time[0],time[1])
        
        
        start =str(request.POST.get('start_time'))
        list2=start.split(' ')
        time1=list2[0].split(':')
        date1=list2[1].split('/')
        print(date1)
        startfin="{}-{}-{} {}:{}".format(date1[-1],date1[-3],date1[-2],time1[0],time1[1])
             
        if form.is_valid():
            binarysignal = form.save(commit = False)
            binarysignal.posted_by = request.user
            binarysignal.expiration_time=final
            binarysignal.starttime  = startfin
            binarysignal.save()
            return redirect('user_dashboard')
        else:
            messages.info(request,'All fields are required!')
            return redirect('add-binary')
    else:
        form = BinaryForm()
        return render(request,'admin_site/add_binary.html',{"form":form})
    
@login_required(login_url="/login_account/")
@permission_required("True", "home")
def forexform(request):
    if request.method == 'POST':
        form = ForexForm(request.POST)
        if form.is_valid():
            forexsignal = form.save(commit= False)
            forexsignal.posted_by = request.user
            forexsignal.save()
            return redirect('user_dashboard')
        else:
            messages.info(request,'All fields are required')
            return redirect('add-forex')
    else:
        form = ForexForm()
        return render(request,'admin_site/add_forex.html',{"form":form})
@login_required()
@permission_required("True", "home")
def user_dashboard(request):    
    return render(request, "admin_site/dashboard.html")

@login_required()
@permission_required("True", "home")
def registered_users(request):
    users = User.objects.all()
    context = {"users": users}
    return render(request, "admin_site/users.html", context)


@login_required()
@permission_required("True", "home")
def user_deactivate(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"{user.username}'s account has been successfully deactivated!")
    return redirect("system_users")


@login_required()
@permission_required("True", "home")
def user_activate(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.username}'s account has been successfully activated!")
    return redirect("system_users")

@login_required()
@permission_required("True","home")
def blogs(request):
    if request.method == 'POST':
        form = BlogForm(request.POST,request.FILES)
        if form.is_valid():
            blog = form.save(commit = False)
            blog.posted_by = request.user
            blog.save()
            return redirect('home')
        else:
            messages.info(request,'All fields are required')
            return redirect('blogs')
    else:
        form = BlogForm()
        context ={
            'form':form,
        }
        return render(request,'admin_site/blog.html',context)
    
#end DASHBOARD

@login_required()
def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logout out!!!")
    return redirect('home')
#------------------------------------------------------------
@login_required()
def view_today_signal(request):
    if Forex.objects.filter(user = request.user) and binary_accounts.objects.filter(user = request.user):
        forexuser = Forex.objects.get(user = request.user)
        binaryuser = binary_accounts.objects.get(user = request.user)
        date = dt.date.today()
        forexSignals = ForexSignals.objects.filter(posted_on__date = date)
        expired =[]
        valid=[]
        binarySignals = BinarySignals.objects.filter(posted_on__date = date)
        for signals in binarySignals:
            datenow = date.time()
            date_now_hours = datenow.hour*60
            date_now_min = datenow.minute
            full_min = date_now_hours + date_now_min
            
            expire_date = signals.expiration_time.time()
            expire_hour = expire_date.hour * 60
            expire_min = expire_date.minute
            full_expire = expire_hour + expire_min
            
            if full_expire - full_min <=  1:
                expired.append(signals)
            else:
                valid.append(signals)
        
        
        
        context = {
            'date':date,
            'valid':binary,
            'expired':binary,
            'forexSignals':forexSignals,
            'forexuser':forexuser,
            'binaryuser':binaryuser,
        }
        return render(request,'signals.html',context)
    elif Forex.objects.filter(user = request.user):
        date = dt.date.today()
        forexuser = Forex.objects.get(user = request.user)
        forexSignals = ForexSignals.objects.filter(posted_on__date = date)
        
        context ={
            'forexuser':forexuser,
            'date':date,
            'forexSignals':forexSignals,
        }
        return render(request,'signals.html',context)
    #error--------------------------------------------
    elif binary_accounts.objects.filter(user = request.user):
        date  = dt.datetime.now()
        date2 = datetime.combine(date.today(), datetime.min.time())
        binaryuser = binary_accounts.objects.get(user = request.user)
        expired =[]
        valid=[]
        binarySignals = BinarySignals.objects.filter(posted_on__date = date)
        for signals in binarySignals:
            datenow = date.time()
            date_now_hours = datenow.hour*60
            date_now_min = datenow.minute
            full_min = date_now_hours + date_now_min
            
            expire_date = signals.expiration_time.time()
            expire_hour = expire_date.hour * 60
            expire_min = expire_date.minute
            full_expire = expire_hour + expire_min
            
            if full_expire - full_min <=  1:
                expired.append(signals)
            else:
                valid.append(signals)
        context = {
            'binaryuser':binaryuser,
            'date':date,
            'expired':expired,
            'valid':valid,
        }
        return render(request,'signals.html',context)
    else :
        return redirect('home')

@login_required()
def view_single_forex_signal(request,id):
    forexuser = Forex.objects.get(user = request.user)
    signal = ForexSignals.objects.get(id = id)
    forexuser = Forex.objects.get(user = request.user)
    date = dt.date.today()
    forexSignals = ForexSignals.objects.filter(posted_on__date = date)
    context = {
        'signal':signal,
        'forexuser':forexuser,
        'date':date,
        
        'forexSignals':forexSignals,
        'forexuser':forexuser,
        
    }
    return render(request,'single_forex.html',context)

@login_required()
def view_single_binary_signal(request,id):
    binaryuser = binary_accounts.objects.get(user = request.user)
    signals = BinarySignals.objects.get(id=id)
    binaryuser = binary_accounts.objects.get(user = request.user)
    date = dt.datetime.now( )
    expired =[]
    valid=[]
    binarySignals = BinarySignals.objects.filter(posted_on__date = date)
    for signals in binarySignals:
        datenow = date.time()
        date_now_hours = datenow.hour*60
        date_now_min = datenow.minute
        full_min = date_now_hours + date_now_min
        
        expire_date = signals.expiration_time.time()
        expire_hour = expire_date.hour * 60
        expire_min = expire_date.minute
        full_expire = expire_hour + expire_min
        
        if full_expire - full_min <=  1:
            expired.append(signals)
        else:
            valid.append(signals)
    context = {
        'signals':signals,
        'date':date,
        'valid':valid,
        'expired':expired,
        
        'binaryuser':binaryuser,
    }
    
    #date difference-------------------------------------------------------------
    
    
    return render(request,'single_binary.html',context)

@login_required(login_url="/login_account/")
def Profiles(request):
    profile = Profile.objects.get(user = request.user)
    
    return render(request,"profile.html",{"profile":profile})
@login_required()
def update_profile(request):
    profile = Profile.objects.get(user = request.user)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST,request.FILES,instance=request.user.profile)
        form1 = UserUpdateform(request.POST,instance=request.user)
        if form.is_valid() and form1.is_valid():
            form1.save() 
            form.save()
            
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=request.user.profile)
        form1 = UserUpdateform(instance=request.user)
    return render(request,"update_profile.html",{"form":form,"form1":form1})
#---------------------------------------------------------
@login_required()
def history_forex(request,number):
    user = Forex.objects.filter(user = request.user)
    if user:
        forex = ForexSignals.objects.all()
        if forex.count() > number:
            forex_histo = ForexSignals.objects.all()[:number]
            return render(request,'history/forex_histo.html',{"forex_histo":forex_histo})
        else:
            messages.info(request,'Thats out of range')
            return redirect('signals')
    else:
        messages.info(request,'you dont have a forex account')
        return redirect('signals')
@login_required()
def history_binary(request,number):
    user = binary_accounts.objects.filter(user = request.user)
    if user:
        binarys = BinarySignals.objects.all()
        if binarys.count() > number:
            binarys_histo = BinarySignals.objects.all()[:number]
            return render(request,'history/binary_histo.html',{"binarys_histo":binarys_histo})
        else:
            messages.info(request,'Thats out of range')
            return redirect('signals')
    else:
        messages.info(request,'You dont have a binary account')
        return redirect('signals')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            
            user=User.objects.get(username = username)
            
            if user:  
                user = User.objects.get(username = username)
                request.session['id'] = user.id
                return redirect('change')
                
            
        except:
            messages.info(request,'this username doesnot exist')
            return redirect('login')
    else:
        return redirect('login')
def change_password(request):
    id = request.session.get('id')
    user = get_object_or_404(User,id = id)
    if request.method == 'POST':
        new_passcode = request.POST['passcode']
        confirmPasscode = request.POST['confirm']
        if new_passcode == confirmPasscode:
            user.password = new_passcode
            user.save()
            
            return redirect('home')
        else:
            messages.info(request,'this fields shoul match!!')
            return redirect('change' )
    else:
        return render(request,'change_password/change_pass.html')
 
def back_home(request):
    return redirect('home')
    
@login_required()
def all_forex(request):
    user = Forex.objects.filter(user = request.user)
    if user:
        forex_histo = ForexSignals.objects.all()
        return render(request,'history/forex_histo.html',{"forex_histo":forex_histo})
        
    else:
        messages.info(request,'you dont have a forex account')
        return redirect('signals')
    
@login_required()
def all_binary(request):
    user = binary_accounts.objects.filter(user = request.user)
    if user:
        binarys_histo = BinarySignals.objects.all()
        return render(request,'history/binary_histo.html',{"binarys_histo":binarys_histo})
        
    else:
        messages.info(request,'You dont have a binary account')
        return redirect('signals')