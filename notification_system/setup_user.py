from app.api_models.models import init_db, SessionLocal, DeviceUserInfo

init_db()
session = SessionLocal()
# write a email address and run this setup_user.py before starting fastapi server and
# then use that email in request body of notify endpoint
user = DeviceUserInfo(email="", settings="UserSettings")
session.add(user)
session.commit()
session.close()
