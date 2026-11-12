from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.role_checker import Role
from app.dependencies.session import SessionDep
from app.models.token import Token
from app.models.user import Register, UserDB
from app.utils.auth import authenticate_user, create_token
from app.utils.db import if_already_exists
from app.utils.normalization import normalize
from app.utils.passwords import hash_password
from app.config import settings
from app.utils.tokens import set_token_expiry

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201)
async def register_user(data: Register, session: SessionDep):
    
    normalized_username = normalize(data.username)
    
    if if_already_exists(normalized_username, session):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exist. Try something else")
        
    hashed_password = hash_password(data.password)
    
    db_user = UserDB(
        username=normalized_username,
        hashed_password=hashed_password,
        role=Role.USER
    )

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Occurred. Terminated") 
    
    return db_user.model_dump(exclude="hashed_password")
    
@router.post("/login", status_code=200)
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    # Authenticate user
    user = authenticate_user(form_data.username, form_data.password, session)
  
    if not user:
     raise HTTPException(status_code=400, detail="Incorrect username or password")
  
    access_token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=set_token_expiry())
    
    return Token(access_token= access_token)