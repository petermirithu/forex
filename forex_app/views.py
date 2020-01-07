from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required


User = get_user_model()


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
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
                user.save()
                
                return redirect('home')
        else:
            messages.info(request,'passwords should match')
            return redirect('register')
        
    else:
        return render(request,'authentication/registration.html')

        
@login_required(login_url = 'accounts/login/')
def home(request):
    return render(request,'index.html')

# Create your views here.
