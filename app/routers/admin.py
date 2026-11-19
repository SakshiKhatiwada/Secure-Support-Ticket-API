from fastapi import APIRouter, Depends, HTTPException, status

from app.data import Role
from app.dependencies.role_checker import RoleChecker
from app.dependencies.session import SessionDep
from app.utils.db import get_all_users_from_db

router = APIRouter(tags=["Admin"])

@router.get("/admin/users", status_code=200, dependencies=[Depends(RoleChecker([Role.ADMIN]))])
def get_users(session: SessionDep):
    # if current_user.role != Role.ADMIN: # RoleChecker implements this 
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="permission denied"
    #     )
    
    return get_all_users_from_db(session)
    
    