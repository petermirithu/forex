from django.conf import settings
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    path('',views.home,name='home'),    
    path('register_account/',views.register,name="register"),       
    url(r'activation_sent/$',views.activation_sent,name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate,name="activate"),
]