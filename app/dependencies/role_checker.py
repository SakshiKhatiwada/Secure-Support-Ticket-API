from enum import Enum

from app.dependencies.user import get_current_user

class Role(str, Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
    
from fastapi import Depends, HTTPException, status

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user = Depends(get_current_user)):

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return True