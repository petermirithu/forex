from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string
from django.core.mail import send_mail

def send_register_confirm_email(name,receiver,domain,uid,token):
  message = Mail(

    from_email='danmuv12@gmail.com',

    to_emails=receiver,

    subject='Welcome to forex...Please Activate Account!',
    html_content=render_to_string('authentication/forexmail.html',{"name":name,"domain":domain,"uid":uid,"token":token})
    
    )
  
  sg = SendGridAPIClient('sendgrid api')

  response = sg.send(message)

  print(response.status_code)


  print(response.body)

  print(response.headers)

 

  
  
  



    

