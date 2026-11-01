from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.session import Base, engine, SessionLocal
from .models.user import SysUser
from .models import core as _core  # noqa: F401  注册核心表模型
from .services.datagen import generate as generate_demo_data
from .core.security import hash_password
from .api.routes import auth, system, analytics, data

app = FastAPI(title="二次元游戏玩家行为分析系统", version="0.1.0-stage1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(system.router)
app.include_router(auth.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(data.router, prefix="/api")

def seed_users():
    db = SessionLocal()
    try:
        for username, pwd, role in [("admin", "admin123", "admin"), ("analyst", "analyst123", "analyst")]:
            if not db.query(SysUser).filter(SysUser.username == username).first():
                db.add(SysUser(username=username, password_hash=hash_password(pwd), role=role))
        db.commit()
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_users()
    db = SessionLocal()
    try:
        result = generate_demo_data(db)
        if not result.get("skipped"):
            print("[datagen] 模拟数据生成完成:", result)
    finally:
        db.close()
