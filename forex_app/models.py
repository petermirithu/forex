from django.db import models
from django.contrib.auth.models import User


class profile(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE)  
  contact=models.CharField(max_length=15,blank=True)  
  signup_confirmation=models.BooleanField(default=False)  
  user_app_id=models.IntegerField(default=0)

  # def __str__(self):
  #   return self.user
  
  @classmethod
  def get_user_profile(cls,user_id):
    result=cls.objects.get(user=user_id)
    return result

class Forex(models.Model):
  user = models.OneToOneField(User,on_delete= models.CASCADE)
  account_type = models.CharField(max_length=50)
  payment = models.IntegerField(default=0)
  date = models.DateTimeField(auto_now_add=True)
  
  
class binary_accounts(models.Model):
  user=models.OneToOneField(User, on_delete=models.CASCADE)
  account_type=models.CharField(max_length=50)
  payment=models.IntegerField(default=0)
  created_date=models.DateField(auto_now_add=True)

  def __str__(self):
      return self.user
  
class Account_price(models.Model):
  price = models.IntegerField(default=1000)
  account_type = models.CharField(max_length=50)
  
  def __str__(self):
    return self.account_type

class ForexSignals(models.Model):
  currency_pair = models.CharField(max_length=700)
  entry_price = models.IntegerField()
  take_profit = models.IntegerField()
  stop_loss = models.IntegerField()
  signal = models.CharField(max_length=900)
  posted_by = models.ForeignKey(User,on_delete= models.CASCADE)
  posted_on = models.DateTimeField(auto_now_add=True)


class BinarySignals(models.Model):
  currency_pair = models.CharField(max_length=700)
  chart_time_frame = models.DateTimeField(auto_now_add=True)
  expiration_time = models.DateTimeField()
  signal = models.CharField(max_length=900)
  posted_by = models.ForeignKey(User,on_delete= models.CASCADE)
  posted_on = models.DateTimeField(auto_now_add=True)
