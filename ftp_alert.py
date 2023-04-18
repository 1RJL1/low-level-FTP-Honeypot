import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_with_attachment(sender_email="ftpalert123@gmail.com", recipient_email="jhontidmath@gmail.com", subject="FTP Honeypot Alert", message="Suspicious activity detected on the FTP honeypot", attachment_path="ftp_log.txt", duration=0):
    
    
    #Include the duration of connection
    message += f"\n\nConnection duration: {duration} seconds"
    

    # Open the attachment file
    with open(attachment_path, 'rb') as f:
        attachment_data = f.read()

    
    #sender_email = "ftpalert123@gmail.com"
    #recipient_email = "jhontidmath@gmail.com"
    #subject = "FTP Honeypot Alert"
    #message = "Suspicious activity detected on the FTP honeypot"
    #attachment_path = "ftp_log.txt"


    # Create the email message object
    message_obj = MIMEMultipart()
    message_obj['From'] = sender_email
    message_obj['To'] = recipient_email
    message_obj['Subject'] = subject

    # Attach the message body
    message_obj.attach(MIMEText(message))

    # Attach the file as an application/octet-stream
    attachment_obj = MIMEApplication(attachment_data, Name='ftp_log.txt')
    attachment_obj['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
    message_obj.attach(attachment_obj)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender_email, 'uewbvymjkqrhvflj')
        smtp.sendmail(sender_email, recipient_email, message_obj.as_string())

