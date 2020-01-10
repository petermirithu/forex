from django.template.loader import render_to_string
from django.core.mail import send_mail

def send_register_confirm_email(name,receiver,domain,uid,token):
  subject='Welcome to forex...Please Activate Account!'
  sender='danmuv12@gmail.com'
  text_content=render_to_string('authentication/forexmail.txt', {"name":name,"domain":domain,"uid":uid,"token":token})
  html_content=render_to_string('authentication/forexmail.html',{"name":name,"domain":domain,"uid":uid,"token":token})
  
  send_mail(subject,text_content,sender,[receiver],html_message=html_content,fail_silently=False)    