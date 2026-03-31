from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user, require_roles

router = APIRouter()

@router.post("/register")
def register(user: User, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == user.email)).first()

    if existing:
        raise HTTPException(status_code=400, detail="User exists")

    user.password = hash_password(user.password)
    session.add(user)
    session.commit()

    return {"msg": "User created"}

@router.post("/login")
def login(user: User, session: Session =  Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user.email, "role": db_user.role, "user_id": db_user.id})
    
    return {"access_token": token, "token_type": "bearer"}
    
    
@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"user":user}    


@router.get("/admin")
def admin_route(user=Depends(require_roles(["admin"]))):
    return {"msg": "Welcome Admin"}