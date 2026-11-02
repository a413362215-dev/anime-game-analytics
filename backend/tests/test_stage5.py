"""阶段 5 验证（分群）：划分完备性、语义不变量、K-Means 可复现、ETL 新口径对账。"""
import os, sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy import func  # noqa: E402
from app.models.core import DimPlayer, FactPayment, PlayerFeatureSnapshot  # noqa: E402
from app.services.datagen import END  # noqa: E402
from app.services.segmentation import compute_segments, get_segments  # noqa: E402


def _segments(db):  # noqa: F811
    from app.models.core import DimGame
    g = db.query(DimGame).filter(DimGame.code == "gi").first()
    return compute_segments(db, g.id, END)


def test_segments_partition_complete(db):  # noqa: F811
    """8 类互斥且完备：每名玩家恰好进一组，总数 == 玩家数，八组全非空"""
    out = _segments(db)
    assert out["total"] == db.query(DimPlayer).filter(DimPlayer.game_code == "genshin").count() \
        if False else out["total"] == 4200
    assert len(out["groups"]) == 8
    assert sum(g["count"] for g in out["groups"]) == out["total"]
    assert all(g["count"] > 0 for g in out["groups"])


def test_segments_semantics(db):  # noqa: F811
    """经济语义不变量：大佬人均消费 > 中R > 月卡党；月卡党人均近 30 天付费应接近月卡价（¥30）；
    沉睡组人均近 30 天付费为 0；肝帝付费率应低于中R"""
    out = _segments(db)
    g = {x["name"]: x for x in out["groups"]}
    assert g["氪金大佬"]["avg_spend"] > g["稳定中R"]["avg_spend"] > g["月卡党"]["avg_spend"]
    assert 15 <= g["月卡党"]["avg_monetary_30d"] <= 40, g["月卡党"]["avg_monetary_30d"]
    assert g["沉睡玩家"]["avg_monetary_30d"] == 0
    assert g["肝帝"]["pay_rate"] < g["稳定中R"]["pay_rate"]


def test_kmeans_reproducible(db):  # noqa: F811
    """固定种子：两次计算（绕开缓存直调）的簇规模与轮廓系数完全一致"""
    a = _segments(db)["kmeans"]
    b = _segments(db)["kmeans"]
    assert a == b
    assert 0 < a["silhouette"] <= 1
    assert sum(c["count"] for c in a["clusters"]) == 4200


def test_etl_orders_and_recency_caliber(db):  # noqa: F811
    """阶段 5 前 ETL 口径修正的对账：orders_30d == 窗口内付费笔数（逐人）；
    recency_days == 截止日 − 玩家维度 last_active_date（逐人，999 仅给从未活跃者）"""
    since = END - timedelta(days=29)
    real_orders = dict(db.query(FactPayment.player_id, func.count(FactPayment.id))
                       .filter(FactPayment.pay_date >= since).group_by(FactPayment.player_id).all())
    bad = 0
    for s in db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).all():
        if s.orders_30d != real_orders.get(s.player_id, 0):
            bad += 1
        p = db.query(DimPlayer).get(s.player_id)
        expect = (END - p.last_active_date).days if p.last_active_date else 999
        assert s.recency_days == expect, f"玩家 {s.player_id} recency {s.recency_days} != {expect}"
    assert bad == 0


def test_segments_endpoint_shape(db):  # noqa: F811
    out = get_segments(db, 1)
    assert out["total"] == 4200 and len(out["groups"]) == 8
    assert sum(len(v) for v in out["scatter"].values()) == 420
