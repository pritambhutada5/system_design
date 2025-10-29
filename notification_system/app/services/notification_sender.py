import os
import smtplib
from email.mime.text import MIMEText
from app.logging.logging_config import setup_logger
from dotenv import load_dotenv
load_dotenv()

notification_sender_logger = setup_logger('notification_sender', 'logs/notification_sender.log')

def send_email(to_email, subject, body, tracking_url = None):
    notification_sender_logger.info(f"Sending email to {to_email} with subject '{subject}'")
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if tracking_url:
        body += f"\n\nTo confirm, please click here: {tracking_url}"

    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        notification_sender_logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        notification_sender_logger.error(f"Failed to send email to {to_email}: {e}")
        return False
