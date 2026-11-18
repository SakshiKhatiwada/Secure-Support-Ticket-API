from fastapi import APIRouter, HTTPException, status

from app.data import Role
from app.dependencies.session import SessionDep
from app.routers.authentication import UserDep
from app.utils.db import get_all_users_from_db

router = APIRouter()

@router.get("/admin/users")
def get_users(current_user: UserDep, session: SessionDep):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission denied"
        )
    
    return get_all_users_from_db(session)
    
    