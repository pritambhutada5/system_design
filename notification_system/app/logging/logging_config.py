import logging
import os

def setup_logger(name, log_file):
    os.makedirs('logs', exist_ok=True)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

app_logger = setup_logger('app', 'logs/app.log')
auth_logger = setup_logger('auth', 'logs/auth.log')
rate_limiter_logger = setup_logger('rate_limiter', 'logs/rate_limiter.log')
