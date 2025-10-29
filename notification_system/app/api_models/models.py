from sqlalchemy import Column, Integer, String, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.logging.logging_config import app_logger
from datetime import datetime
from sqlalchemy import ForeignKey


DATABASE_URL = "sqlite:///./users.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class DeviceUserInfo(Base):
    __tablename__ = "device_user_info"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    settings = Column(String)


class NotificationLog(Base):
    __tablename__ = "notification_log"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    subject = Column(String)
    message = Column(String)
    sent = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error = Column(String, nullable=True)

def log_notification(email, subject, message, sent, error=None):
    session = SessionLocal()
    try:
        log_entry = NotificationLog(
            email=email, subject=subject, message=message, sent=sent, error=error
        )
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        log_id = log_entry.id
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
    return log_id


class NotificationClick(Base):
    __tablename__ = "notification_click"
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notification_log.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

def log_click(notification_id):
    session = SessionLocal()
    click_entry = NotificationClick(notification_id=notification_id)
    session.add(click_entry)
    session.commit()
    session.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    app_logger.info("Database initialized")
