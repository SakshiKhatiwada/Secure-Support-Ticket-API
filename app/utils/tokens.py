from datetime import datetime, timezone, timedelta
import jwt

from app.config import settings

def set_token_expiry() -> timedelta:   
    access_token_expires = timedelta(minutes=settings.token_expiry_time)
    return access_token_expires