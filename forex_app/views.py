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
from .models import *
from .forms import *
from django.contrib.auth.hashers import check_password
import random
from django.conf import settings
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse

from django.contrib.auth.decorators import permission_required


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

                forex_site = get_current_site(request)
                domain = forex_site.domain
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                send_register_confirm_email(
                    username, email, domain, uid, token)
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
                user_profile = profile.get_user_profile(user_x.id)
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

# selecting account
@login_required(login_url="/login_account/")
def select_account(request):
    title = 'Select account'
    context = {
        'title': title
    }
    return render(request, 'select_acc.html', context)


@login_required(login_url="/login_account/")
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
                id_gen = random.randint(0000000, 9999999)
                user_profile = profile.objects.get(user=user_exists)
                user_profile.user_app_id = id_gen
                user_profile.save()

                user_binary_acc = binary_accounts(
                    user=request.user, account_type=acc_type, payment=0)
                user_binary_acc.save()
                return redirect('home')
        except User.DoesNotExist:
            messages.info(request, 'Please enter a valid email!')
            return redirect('select_account')


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
                    user_profile = profile.objects.get(user=user)
                    user_profile.user_app_id = id_forex
                    user_profile.save()

                    user_forex = Forex(user=request.user,
                                    account_type=acc_type, payment=0)
                    user_forex.save()
                    return redirect('home')
                else:
                    request.session['order_id'] = acc_type
                    return redirect('process_payment')
                
        except User.DoesNotExist:
            messages.info(request, 'please enter a valid email')
            return redirect('select_account')


# selecting account over

@login_required(login_url="/login_account/")
def home(request):
    try:
        account_user = Forex.objects.get(user=request.user)
        if account_user:
            messages.info(
                request, f'Good to see you in {account_user.account_type} forex account!')
            return render(request, 'index.html')

    except Forex.DoesNotExist:
        try:
            account_user = binary_accounts.objects.get(user=request.user)
            if account_user:
                messages.info(
                    request, f'Good to see you in {account_user.account_type} binary account!')
                return render(request, 'index.html')

        except binary_accounts.DoesNotExist:
            return redirect('select_account')


# paypal  process


def process_payment(request):

    order_id = request.session.get('order_id')
    if order_id=='forexsilver':
        vari_x='Forex'        
        account_type = get_object_or_404(Account_price, account_type=vari_x)

        host = request.get_host()

        paypal_dict = {

            'business': settings.PAYPAL_RECEIVER_EMAIL,

            'amount': '%.2f' % account_type.price,

            'item_name': 'Order {}'.format(account_type.account_type),

            'invoice': str(random.randint(00000,99999)),

            'currency_code': 'USD',
            
            'notify_url': '{}/q-forex-binary-f-k-defw-dshsgdtdhvdsss-scczzc-url/'.format(host),

            'return_url': '{}/payment-done/'.format(host),

            'cancel_return': '{}/payment-cancelled/'.format(host),
        }



        form = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'paypal/process_payment.html', {'account_type': account_type, 'form': form})
    
    else:
        vari_y='Binary'
        account_type = get_object_or_404(Account_price, account_type=vari_y)
        host = request.get_host()
        paypal_dict = {

            'business': settings.PAYPAL_RECEIVER_EMAIL,

            'amount': '%.2f' % account_type.price,

            'item_name': 'Order {}'.format(account_type.account_type),

            'invoice': str(random.randint(00000,99999)),

            'currency_code': 'USD',
            
            'notify_url': '{}/q-forex-binary-f-k-defw-dshsgdtdhvdsss-scczzc-url/'.format(host),

            'return_url': '{}/payment-done/'.format(host),

            'cancel_return': '{}/payment-cancelled/'.format(host),
        }

        form = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'paypal/process_payment.html', {'account_type': account_type, 'form': form})
    
@csrf_exempt
def payment_done(request):
    args={'post':request.POST,'get':request.GET}
    account_ty = request.POST.get('item_name')
    if account_ty=='Forex':
        user_x=Forex(user=request.user,account_type=account_ty,payment=10)
        user_x.save()
    elif account_ty=='Binary':
        user_x=binary_accounts(user=request.user,account_type=account_ty,payment=10)    
        user_x.save()
        
    return render(request, 'paypal/payment_done.html',args)
 
 
@csrf_exempt
def payment_canceled(request):
    args={'post':request.POST,'get':request.GET}
    return render(request, 'paypal/payment_cancelled.html',args)

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
                
        if form.is_valid():
            binarysignal = form.save(commit = False)
            binarysignal.posted_by = request.user
            binarysignal.expiration_time=final
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
def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logout out!!!")
    return redirect('home')
    
