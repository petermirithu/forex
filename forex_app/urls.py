from django.conf import settings
from django.urls import path,include
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('accounts/',include('registration.backends.simple.urls')),
]