from sqlalchemy import Column, Integer, String, DateTime, func
from ..db.session import Base

class SysUser(Base):
    """系统用户表 sys_user（30 表设计中的第一层）"""
    __tablename__ = "sys_user"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False, default="analyst")  # admin / analyst / operator
    status = Column(String(16), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now())
