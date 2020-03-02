from django.conf import settings
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib.auth import views as auth_view


urlpatterns = [
    path('',views.home,name='home'),    
    url(r'^register_account/$',views.register,name="register"),       
    url(r'^login_account/$',views.login_user,name="login_user"),       
    url(r'^logout_account/$',views.logout_request,name="logout_user"),       
    url(r'activation_sent/$',views.activation_sent,name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate,name="activate"),
    path('accounts/login/',views.back_home,name="back"),
    

    
    url(r'select_account/$',views.select_account,name="select_account"),
    path('select_account/forex/<str:acc_type>/',views.forex_account_type,name="forex_acc"),
    path('select_account/binary/<str:acc_type>/',views.binary_account_type,name="binary_acc"),    
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
    url(r'^q-forex-binary-f-k-defw-dshsgdtdhvdsss-scczzc-url/',include('paypal.standard.ipn.urls')),
    path('single/forex/signal/<int:id>',views.view_single_forex_signal,name="single-forex"),
    path('single/binary/signal/<int:id>',views.view_single_binary_signal,name="single-binary"),
    path('signals/',views.view_today_signal,name="signals"),
    path('profile/',views.Profiles,name="profile"),
    path('update/profile/',views.update_profile,name="update"),
    path('forgot/password/',views.forgot_password,name="forgot"),
    path('change/password/',views.change_password,name="change"),
    path('accounts/profile/',views.home,name="later"),
    path('history-forex/<int:number>/',views.history_forex,name="history-forex"),
    path('history-binary/<int:number>/',views.history_binary,name="history-binary"),
    path('history-forex/',views.all_forex,name="all-forex"),
    path('history-binary/',views.all_binary,name="all-binary"),
    
    
    # admin
    path("dashboard/", views.user_dashboard, name="user_dashboard"),    
    path("users/", views.registered_users, name="system_users"),
    path('activate/user/<int:user_id>', views.user_activate, name='activate_user'),
    path('deactivate/user/<int:user_id>', views.user_deactivate, name='deactivate_user'),  
    path('add/forex/signals/',views.forexform,name='add-forex'), 
    path('add/binary/signals/',views.binaryform,name='add-binary'), 
    path("blogs/",views.blogs,name="blogs"),
    url(r'^logout/$',views.logout_user,name='logout')
]
