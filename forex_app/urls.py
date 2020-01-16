from django.conf import settings
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    path('',views.home,name='home'),    
    url(r'^register_account/$',views.register,name="register"),       
    url(r'^login_account/$',views.login_user,name="login"),       
    url(r'^logout_account/$',views.logout_request,name="logout"),       
    url(r'activation_sent/$',views.activation_sent,name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate,name="activate"),
    url(r'select_account/$',views.select_account,name="select_account"),
    path('select_account/forex/<str:acc_type>/',views.forex_account_type,name="forex_acc"),
    path('select_account/binary/<str:acc_type>/',views.binary_account_type,name="binary_acc"),    
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
    
    
]
