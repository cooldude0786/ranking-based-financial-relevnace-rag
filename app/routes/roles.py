from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db import get_session
from app.models import User
from app.dependencies import require_roles
from app.permission import ROLE_PERMISSIONS

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/assign-role")
def assign_role(user_id: int,
                role: str,
                session: Session = Depends(get_session),
                admin=Depends(require_roles(["admin"]))):

    user = session.get(User, user_id)
    user.role = role
    session.commit()

    return {"msg": "Role assigned"}

@router.get("/user/{user_id}")
def get_user_role(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return {"role": user.role}



@router.get("/users/{user_id}/permissions")
def get_permissions(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return {"permissions": ROLE_PERMISSIONS[user.role]}