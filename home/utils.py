import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, from_email, recipient_list):
    # Set up the SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # For TLS
    smtp_username = 'fashion.stylehub.info@gmail.com'
    smtp_password = 'shaurya@vaibhav'

    # Create a message object
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)
    msg['Subject'] = subject

    # Add the message body
    body = MIMEText(message, 'html')
    msg.attach(body)

    # Create an SMTP object and send the message
    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.starttls()
    smtp_obj.login(smtp_username, smtp_password)
    smtp_obj.sendmail(from_email, recipient_list, msg.as_string())
    smtp_obj.set_debuglevel(1)

    smtp_obj.quit()
