"""数据管理接口：数据源列表、同步任务、文件导入（UIGF/SRGF）。"""
import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.core import DataSource, SyncTask
from ...datasources.uigf import UigfDataSource

router = APIRouter(tags=["data"])


@router.get("/data/sources")
def sources(db: Session = Depends(get_db)):
    rows = db.query(DataSource).order_by(DataSource.id).all()
    return [{"code": s.code, "name": s.name, "kind": s.kind, "status": s.status,
             "description": s.description, "total_rows": s.total_rows or 0,
             "last_sync_at": s.last_sync_at.strftime("%m-%d %H:%M") if s.last_sync_at else "尚未同步"}
            for s in rows]


@router.get("/data/tasks")
def tasks(db: Session = Depends(get_db)):
    rows = (db.query(SyncTask, DataSource.name).join(DataSource, DataSource.id == SyncTask.source_id)
            .order_by(SyncTask.id.desc()).limit(12).all())
    return [{"title": t.title, "source": src_name, "added": t.added_rows, "skipped": t.skipped_rows,
             "status": t.status, "detail": t.detail,
             "time": t.started_at.strftime("%m-%d %H:%M") if t.started_at else ""}
            for t, src_name in rows]


@router.post("/ingest/gacha")
async def ingest_gacha(file: UploadFile = File(...), game: str = Form("gi")):
    """导入 UIGF（原神）/ SRGF（星穹铁道）抽卡记录文件；重复导入自动去重。"""
    raw = await file.read()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {"error": "文件不是合法的 JSON（UIGF/SRGF 导出文件应为 JSON 格式）"}
    return UigfDataSource().import_payload(payload, game)
