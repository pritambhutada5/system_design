from app.logging.logging_config import setup_logger
from app.api_models.models import log_notification, log_click

analytics_logger = setup_logger('analytics', 'logs/analytics.log')

def report_delivery(email, subject, message, success, error=None):
    analytics_logger.info(f"Delivered: {email} Subject: {subject} Success: {success} Error: {error}")
    log_notification(email, subject, message, sent=success, error=error)

def track_click(notification_id):
    analytics_logger.info(f"Click tracked for notification {notification_id}")
    log_click(notification_id)
