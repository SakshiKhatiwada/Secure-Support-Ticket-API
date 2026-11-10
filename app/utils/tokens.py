from datetime import datetime, timezone, timedelta
import jwt

from app.config import settings

def create_access_token(user_id: int)-> str:
    now = datetime.now(timezone.utc)
    
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.token_expiry_time)
        }
    
    token = jwt.encode(
        payload,
        settings.signature_key,
        algorithm="HS256"
    )
    
    return token