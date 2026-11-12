from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

# import jwt

from app.dependencies.session import SessionDep
from app.models.token import Token
from app.config import settings
from app.utils.db import get_user_from_db

from jose import jwt, JWTError
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# -------var
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["argon2"], deprecated='auto')

#-----

def create_token(data: dict, expires_delta: timedelta | None = None) -> Token:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.signature_key, algorithm=settings.algorithm)
    return encoded_jwt

def authenticate_user(username: str, password: str, session:SessionDep):
    user = get_user_from_db(username, session)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Username or Password") # we shouldn't give info whether the username is wrong or password
    
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Username or Password")
    return user
    