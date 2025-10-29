from queue import Queue
from threading import Thread
from app.services.notification_sender import send_email
from app.logging.logging_config import setup_logger
from app.services.analytics import report_delivery
from app.api_models.models import log_notification

worker_logger = setup_logger('worker', 'logs/worker.log')
notification_queue = Queue()
_worker_thread = None
MAX_RETRIES = 3


def notification_worker():
    while True:
        task = notification_queue.get()
        if task is None:  # Sentinel for shutdown
            worker_logger.info("Worker received shutdown signal")
            break

        try:
            email, subject, message = task['email'], task['subject'], task['message']
            retries = task.get('retries', 0)
            worker_logger.info(f"Worker processing notification for {email}")

            # Log notification and get ID
            notif_id = log_notification(email, subject, message, sent=False)
            tracking_url = f"http://127.0.0.1:8000/track_click/{notif_id}"

            success = send_email(email, subject, message, tracking_url)
            error = None if success else "Email send failed"

            report_delivery(email, subject, message, success, error)
            if not success and retries < MAX_RETRIES:
                worker_logger.info(f"Retrying notification for {email}, retry count {retries+1}")
                task['retries'] = retries + 1
                notification_queue.put(task)
        except Exception as e:
            worker_logger.error(f"Error in worker: {e}")

def start_worker():
    global _worker_thread
    _worker_thread = Thread(target=notification_worker, daemon=True)
    _worker_thread.start()
    worker_logger.info("Worker started")
    return _worker_thread

def stop_worker():
    global _worker_thread
    notification_queue.put(None)  # Push sentinel to trigger shutdown
    if _worker_thread:
        _worker_thread.join()
        worker_logger.info("Worker stopped")
