from app.logging.logging_config import app_logger

cache = {}

def get_user_from_cache(email):
    user = cache.get(email)
    app_logger.info(f"Cache get for email {email}: {'Hit' if user else 'Miss'}")
    return user

def set_user_in_cache(email, data):
    cache[email] = data
    app_logger.info(f"Cache set for email {email}")
