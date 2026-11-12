from app.dependencies.session import get_session
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import Depends, HTTPException
from sqlmodel import Session
from app.models.user import UserPublic
from jwt.exceptions import InvalidTokenError
from app.config import settings

from app.utils.auth import oauth2_scheme
from app.utils.db import get_user_from_db

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(
            token,
            settings.signature_key,
            algorithms="HS256",
            options={"require": ["sub", "exp"]}
        )
        
        username = payload["sub"]
    except(InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Bad Request: Invalid Header or expired tokan")
    
    user = get_user_from_db(username=username, session=session)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Bad Request, Account Disabled.")
    
    return user