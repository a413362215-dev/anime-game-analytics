"""全套件共享夹具：整个测试会话只建一个测试库（session 级）。

教训（阶段 4 踩到）：早期把夹具写在某个测试模块里、其他模块 import 复用，
每个模块都会各自再建一份 13MB 的完整数据库——/tmp（512MB tmpfs）被塞满，
报 database or disk is full。共享数据层测试的标准做法就是 conftest + session 级单库。
"""
import os, sys, tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import Base  # noqa: E402
from app.models.user import SysUser  # noqa: E402,F401
from app.services.datagen import generate  # noqa: E402


@pytest.fixture(scope="session")
def db():
    tmpdir = tempfile.mkdtemp(prefix="aga-test-", dir=os.path.expanduser("~/workspace"))
    engine = create_engine(f"sqlite:///{tmpdir}/test.db")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    result = generate(session)
    assert not result.get("skipped"), "测试库生成失败"
    yield session
    session.close()
