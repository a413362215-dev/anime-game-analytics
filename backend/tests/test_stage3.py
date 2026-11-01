"""阶段 3 验证增量：ETL 快照对账 + 漏斗口径。复用阶段 2 的测试库夹具。"""
import os, sys
from datetime import timedelta
import pytest
from sqlalchemy import func

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.models.core import DimPlayer, FactPayment, FactGacha, FactEventLog, PlayerFeatureSnapshot  # noqa: E402
from app.services.datagen import END  # noqa: E402
from app.services.etl import run_feature_snapshot, verify_daily_metrics  # noqa: E402


def test_snapshot_monetary_matches_payments(db):  # noqa: F811
    """快照 monetary_30d 必须等于该玩家近 30 天付费流水之和（ETL 对账）"""
    since = END - timedelta(days=29)
    money = dict(db.query(FactPayment.player_id, func.sum(FactPayment.amount))
                 .filter(FactPayment.pay_date >= since).group_by(FactPayment.player_id).all())
    bad = 0
    for s in db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).all():
        if abs((money.get(s.player_id, 0) or 0) - s.monetary_30d) > 0.51:
            bad += 1
    assert bad == 0, f"{bad} 名玩家快照金额对不上"


def test_snapshot_pulls_match_gacha(db):  # noqa: F811
    since = END - timedelta(days=29)
    pulls = dict(db.query(FactGacha.player_id, func.count(FactGacha.id))
                 .filter(FactGacha.pull_date >= since).group_by(FactGacha.player_id).all())
    bad = sum(1 for s in db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).all()
              if pulls.get(s.player_id, 0) != s.gacha_pulls_30d)
    assert bad == 0, f"{bad} 名玩家快照抽卡数对不上"


def test_etl_idempotent(db):  # noqa: F811
    n0 = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).count()
    run_feature_snapshot(db, END)
    n1 = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).count()
    assert n0 == n1 and n0 > 0


def test_daily_metrics_verify_clean(db):  # noqa: F811
    out = verify_daily_metrics(db)
    assert all(v["revenue_mismatch_days"] == 0 and v["new_users_mismatch_days"] == 0
               for v in out.values()), out


def test_funnel_counts_from_events(db):  # noqa: F811
    """漏斗口径：近 30 日注册玩家中，各步到达人数 == 事件去重计数，且单调不增"""
    import json
    from app.models.core import DimGame
    for g in db.query(DimGame).all():
        start = END - timedelta(days=29)
        pids = [pid for (pid,) in db.query(DimPlayer.id).filter(
            DimPlayer.game_id == g.id, DimPlayer.register_date >= start).all()]
        counts = {}
        for props, c in (db.query(FactEventLog.props, func.count(func.distinct(FactEventLog.player_id)))
                         .filter(FactEventLog.event_name == "tutorial_step",
                                 FactEventLog.player_id.in_(pids)).group_by(FactEventLog.props).all()):
            counts[json.loads(props)["step"]] = c
        vals = [counts.get(i, 0) for i in range(1, 7)]
        assert vals[0] == len(pids), f"{g.code} 第一步应等于窗口内新玩家数"
        assert all(vals[i] >= vals[i + 1] for i in range(5)), f"{g.code} 漏斗不单调 {vals}"
