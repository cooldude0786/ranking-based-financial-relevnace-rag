from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db import get_session
from app.models import User, UserRole
from app.dependencies import require_roles
from app.permission import ROLE_PERMISSIONS

router = APIRouter(tags=["Roles & Users"])

# Roles endpoints
roles_router = APIRouter(prefix="/roles", tags=["Roles"])

@roles_router.post("/create")
def create_role(role_name: str,
                session: Session = Depends(get_session),
                admin=Depends(require_roles(["admin"]))):
    
    try:
        UserRole(role_name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role. Available roles: admin, analyst, auditor, client")
    
    return {"msg": "Role created", "role": role_name}

# Users endpoints
users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.post("/assign-role")
def assign_role(user_id: int,
                role: str,
                session: Session = Depends(get_session),
                admin=Depends(require_roles(["admin"]))):

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate role
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role. Available roles: admin, analyst, auditor, client")
    
    user.role = role
    session.commit()

    return {"msg": "Role assigned", "user_id": user_id, "role": role}

@users_router.get("/{id}/roles")
def get_user_roles(id: int, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"role": user.role}

@users_router.get("/{id}/permissions")
def get_permissions(id: int, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"permissions": ROLE_PERMISSIONS.get(user.role, [])}

router = APIRouter()
router.include_router(roles_router)
router.include_router(users_router)