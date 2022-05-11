# import necessary packages
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import string

# creates the messege object and sets the sender
def msg_setup():
    msg = MIMEMultipart()
    msg['From'] = "flourishappdrexel@gmail.com"

    return msg

def setup_mailer(msg):
    msg = msg_setup()
    password = "Flourish2022"

    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    return server

def send_email(message: str, subject: str, to: str):
    msg = msg_setup()

    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = setup_mailer(msg)
    
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("successfully sent email to %s:" % (msg['To']))

