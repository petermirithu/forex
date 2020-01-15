from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('person_portfolio.urls')),
    path('admin/', admin.site.urls),
]