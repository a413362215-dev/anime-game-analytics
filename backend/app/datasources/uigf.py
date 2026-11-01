"""UIGF / SRGF 抽卡记录导入适配器。

UIGF 是原神抽卡记录的社区标准导出格式（SRGF 为星穹铁道对应标准），
结构：{"info": {"uid": ..., "lang": ...}, "list": [{id, uid, gacha_type, item_id, rank_type, time, name, ...}]}
去重：以记录自带 id 作为 fact_gacha.external_id，靠唯一约束 + 预查跳过，
同一文件重复导入不会重复入库（返回 skipped 计数）。
安全：导出文件里的 authkey 只用于一次性导入，本适配器不读取、不存储、不打日志。
"""
import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from .base import BaseDataSource
from ..models.core import DimPlayer, DimItem, FactGacha, DataSource, SyncTask
from ..db.session import SessionLocal

BANNER_TYPE_MAP = {  # UIGF gacha_type → 标准 banner_type
    "301": "character", "400": "character", "302": "weapon", "200": "standard", "100": "standard",
    "11": "character", "12": "weapon", "1": "standard", "2": "standard",  # SRGF 跃迁类型
}


class UigfDataSource(BaseDataSource):
    name = "uigf"
    supported = ["gacha_log", "player", "item"]

    def test_connection(self, config: dict) -> bool:
        return isinstance(config.get("payload"), dict) and "list" in config["payload"]

    def fetch_raw(self, config: dict):
        return config["payload"]

    def transform(self, raw, mapping: dict):
        return raw["list"]

    def import_payload(self, payload: dict, game_code: str) -> dict:
        db: Session = SessionLocal()
        try:
            from ..models.core import DimGame
            game = db.query(DimGame).filter(DimGame.code == game_code).first()
            if not game:
                return {"error": f"unknown game: {game_code}"}
            src_code = "uigf" if game_code == "gi" else "srgf"
            src = db.query(DataSource).filter(DataSource.code == src_code).first()
            rows = payload.get("list", [])
            existing = {e for (e,) in db.query(FactGacha.external_id)
                        .filter(FactGacha.game_id == game.id, FactGacha.external_id.isnot(None)).all()}
            item_cache, player_cache = {}, {}
            added = skipped = 0
            batch = []
            for r in rows:
                ext = str(r.get("id") or "")
                if not ext or ext in existing:
                    skipped += 1
                    continue
                existing.add(ext)
                uid = str(r.get("uid") or payload.get("info", {}).get("uid") or "unknown")
                if uid not in player_cache:
                    p = db.query(DimPlayer).filter(DimPlayer.game_id == game.id,
                                                   DimPlayer.external_uid == uid).first()
                    if not p:
                        from datetime import date
                        p = DimPlayer(game_id=game.id, external_uid=uid, nickname=f"导入玩家{uid[-4:]}",
                                      channel="import", register_date=date(2026, 1, 1))
                        db.add(p); db.flush()
                    player_cache[uid] = p.id
                item_ext = str(r.get("item_id") or "0")
                if item_ext not in item_cache:
                    it = db.query(DimItem).filter(DimItem.game_id == game.id,
                                                  DimItem.external_item_id == item_ext).first()
                    if not it:
                        it = DimItem(game_id=game.id, external_item_id=item_ext,
                                     name=r.get("name") or f"物品{item_ext}",
                                     item_type="character", rarity=int(r.get("rank_type") or 3))
                        db.add(it); db.flush()
                    item_cache[item_ext] = it.id
                try:
                    pulled = datetime.fromisoformat(str(r.get("time")).replace(" ", "T"))
                except ValueError:
                    skipped += 1
                    continue
                batch.append({"game_id": game.id, "player_id": player_cache[uid], "banner_id": None,
                              "item_id": item_cache[item_ext], "source_id": src.id if src else None,
                              "external_id": ext,
                              "banner_type": BANNER_TYPE_MAP.get(str(r.get("gacha_type")), "character"),
                              "rarity": int(r.get("rank_type") or 3), "pity_count": 0,
                              "pulled_at": pulled, "pull_date": pulled.date()})
                added += 1
            if batch:
                db.bulk_insert_mappings(FactGacha, batch)
            if src:
                src.total_rows = (src.total_rows or 0) + added
                src.last_sync_at = datetime.now()
            db.add(SyncTask(source_id=src.id if src else 1,
                            title=f"{'原神 UIGF' if game_code == 'gi' else '星穹铁道 SRGF'} 导入",
                            added_rows=added, skipped_rows=skipped, status="success",
                            detail=f"文件记录 {len(rows)} 条"))
            db.commit()
            return {"added": added, "skipped": skipped, "total_in_file": len(rows)}
        finally:
            db.close()


def feedback_csv_external_id(content: str, created_at: str) -> str:
    return hashlib.md5(f"{content}|{created_at}".encode()).hexdigest()[:24]
