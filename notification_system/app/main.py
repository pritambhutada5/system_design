from fastapi import FastAPI, Depends
from app.logging.logging_config import app_logger
from app.services.auth import authenticate
from app.services.rate_limiter import rate_limiter
from app.api_models.models import init_db, SessionLocal, DeviceUserInfo
from app.services.cache import get_user_from_cache, set_user_in_cache
from pydantic import BaseModel
from app.services.worker import notification_queue, start_worker, stop_worker
from app.services.analytics import track_click



class NotifyRequest(BaseModel):
    email: str
    message: str

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_worker()

@app.on_event("shutdown")
async def shutdown_event():
    stop_worker()


init_db()


@app.post('/notify')
async def notify(req: NotifyRequest, user=Depends(authenticate)):
    email = req.email
    message = req.message
    subject = "Notification"
    api_key = user
    rate_limiter(api_key)

    # Load user info from cache or DB
    user_info = get_user_from_cache(email)
    if not user_info:
        db = SessionLocal()
        db_user = db.query(DeviceUserInfo).filter(DeviceUserInfo.email == email).first()
        if db_user:
            user_info = {"email": db_user.email, "settings": db_user.settings}
            set_user_in_cache(email, user_info)
            db.close()
    if not user_info:
        app_logger.warning(f"User not found: {email}")
        return {"status": "error", "reason": "User not found"}

    app_logger.info(f"Notification accepted for {email}")
    task = {"email": email, "subject": subject, "message": message}
    notification_queue.put(task)
    app_logger.info(f"Notification enqueued for {email}")

    return {"status": "queued", "email": email}


@app.get("/track_click/{notification_id}")
def track_click_endpoint(notification_id: int):
    track_click(notification_id)
    return {"status": "click tracked", "notification_id": notification_id}
