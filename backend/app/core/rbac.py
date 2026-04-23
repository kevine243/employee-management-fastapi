from fastapi import Depends, HTTPException, status
from app.dependencies import get_current_user

class RoleChecker:
    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles

    def __call__(self, user=Depends(get_current_user)):
        user_roles = {role.name.value for role in user.roles}
        if not user_roles.intersection(self.required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: insufficient role privileges "
            )
        return user

# Raccourcis
require_admin  = RoleChecker(["admin"])
require_editor = RoleChecker(["admin", "editor"])