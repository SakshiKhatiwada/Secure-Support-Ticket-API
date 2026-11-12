from sqlite3 import IntegrityError

from fastapi import APIRouter, HTTPException, status
from app.dependencies.role_checker import Role
from app.dependencies.session import SessionDep
from app.models.user import Register, UserDB
from app.utils.db import if_already_exists
from app.utils.normalization import normalize
from app.utils.passwords import hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
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
    
