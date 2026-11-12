from typing import Annotated

from app.data import Role
from app.dependencies.user import get_current_user
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
    
AdminOnly = Annotated[
    bool,
    Depends(RoleChecker([Role.ADMIN]))
]

StaffOrAdmin = Annotated[
    bool,
    Depends(RoleChecker([Role.STAFF, Role.ADMIN]))
]

AllAccess = Annotated[
    bool,
    Depends(RoleChecker([Role.ADMIN, Role.STAFF, Role.USER]))
]