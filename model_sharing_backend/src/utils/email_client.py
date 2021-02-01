import smtplib
from email.message import EmailMessage

__sender_email = "inof@gmx.com"
__auth_secret = "Z28sLGCxdPXAuRu"
__smtp_server_url = 'mail.gmx.com'


def send_reset_password_email(receiver_email, receiver_name, reset_code):
    msg = EmailMessage()
    msg['From'] = __sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Password Reset'
    msg_text = f'''
            Dear {receiver_name},
            
                Your password reset code is {reset_code}. Please, use it to change your password within 15 minutes.
                
                Regards
                The INoF Team'''
    msg.set_content(msg_text)

    server = smtplib.SMTP(__smtp_server_url, 587)
    server.starttls()
    server.login(__sender_email, __auth_secret)
    server.sendmail(__sender_email, receiver_email, msg.as_string())
    server.quit()
