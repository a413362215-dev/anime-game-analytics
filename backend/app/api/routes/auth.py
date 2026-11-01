import random, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import SysUser
from ...schemas.auth import LoginIn, TokenOut, RegisterIn, SmsSendIn, SmsLoginIn, ResetIn
from ...core.security import verify_password, hash_password, create_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# 演示环境验证码仓库：phone -> (code, expire_ts)
# 正式环境应换成真实短信服务商 + Redis 存储，接口形状不变
_sms_codes: dict[str, tuple[str, float]] = {}

def _issue_code(phone: str) -> str:
    code = f"{random.randint(0, 999999):06d}"
    _sms_codes[phone] = (code, time.time() + 300)
    return code

def _check_code(phone: str, code: str) -> bool:
    item = _sms_codes.get(phone)
    if not item or item[1] < time.time() or item[0] != code:
        return False
    del _sms_codes[phone]
    return True

def _token_out(user: SysUser) -> TokenOut:
    return TokenOut(access_token=create_token(user.id, user.username, user.role),
                    username=user.username, role=user.role)

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(SysUser).filter(SysUser.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return _token_out(user)

@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(SysUser).filter(SysUser.username == body.username).first():
        raise HTTPException(status_code=400, detail="该账号已被注册")
    if body.phone and db.query(SysUser).filter(SysUser.phone == body.phone).first():
        raise HTTPException(status_code=400, detail="该手机号已被绑定")
    user = SysUser(username=body.username, password_hash=hash_password(body.password),
                   phone=body.phone, role="analyst")
    db.add(user); db.commit(); db.refresh(user)
    return _token_out(user)

@router.post("/sms/send")
def sms_send(body: SmsSendIn):
    if len(body.phone) < 6:
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    code = _issue_code(body.phone)
    # dev_mode 下把验证码回显给前端方便演示；接真实短信后必须去掉 demo_code
    return {"sent": True, "dev_mode": True, "demo_code": code, "expires_in": 300}

@router.post("/sms/login", response_model=TokenOut)
def sms_login(body: SmsLoginIn, db: Session = Depends(get_db)):
    if not _check_code(body.phone, body.code):
        raise HTTPException(status_code=401, detail="验证码错误或已过期")
    user = db.query(SysUser).filter(SysUser.phone == body.phone).first()
    if not user:
        # 短信登录未注册自动建号（现代登录的通行做法）
        user = SysUser(username=f"u_{body.phone}", password_hash=hash_password(f"sms-{body.phone}-{random.random()}"),
                       phone=body.phone, role="analyst")
        db.add(user); db.commit(); db.refresh(user)
    return _token_out(user)

@router.post("/password/reset")
def password_reset(body: ResetIn, db: Session = Depends(get_db)):
    user = db.query(SysUser).filter(SysUser.username == body.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号不存在")
    if not _check_code(body.phone, body.code):
        raise HTTPException(status_code=401, detail="验证码错误或已过期")
    user.password_hash = hash_password(body.new_password)
    if not user.phone:
        user.phone = body.phone
    db.commit()
    return {"reset": True}

@router.get("/me")
def me(user: SysUser = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role, "phone": user.phone}
