from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import SysUser
from ...schemas.auth import LoginIn, TokenOut
from ...core.security import verify_password, create_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(SysUser).filter(SysUser.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenOut(access_token=create_token(user.id, user.username, user.role),
                    username=user.username, role=user.role)

@router.get("/me")
def me(user: SysUser = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}
