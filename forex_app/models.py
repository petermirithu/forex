from django.db import models
from django.contrib.auth.models import User

class profile(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE)  
  contact=models.CharField(max_length=15,blank=True)  
  signup_confirmation=models.BooleanField(default=False)
  

  # def __str__(self):
  #   return self.user
  

