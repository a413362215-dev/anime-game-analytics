"""阶段 3 验证（第二轮）：ETL 快照全字段对账、快照版本化、漏斗接口口径。

口径与阶段 2 验证套件一致：能从事实表独立重算的，一个字段一个字段对；
接口层直接调用路由函数校验返回结构与自洽性，另有真实服务冒烟（见验证报告）。
"""
import os, sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy import func  # noqa: E402
from app.models.core import (DimPlayer, FactSession, PlayerFeatureSnapshot)  # noqa: E402
from app.services.datagen import END  # noqa: E402
from app.services.etl import run_feature_snapshot  # noqa: E402
from app.api.routes.analytics import funnel, STEP_NAMES  # noqa: E402


def _sessions_by_player(db):  # noqa: F811
    out = {}
    for pid, d, dur in db.query(FactSession.player_id, FactSession.session_date,
                                FactSession.duration_min).all():
        out.setdefault(pid, []).append((d, dur or 0))
    return out


def test_snapshot_frequency_avg_recency_match(db):  # noqa: F811
    """频次=窗口内去重会话天数；平均时长=窗口内会话均值；最近活跃=截止日-最后会话日"""
    since = END - timedelta(days=29)
    sess = _sessions_by_player(db)
    bad = []
    for s in db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).all():
        rows = sess.get(s.player_id, [])
        win = [(d, dur) for d, dur in rows if d >= since]
        exp_freq = len({d for d, _ in win})
        exp_avg = round(sum(dur for _, dur in win) / len(win), 1) if win else 0
        exp_rec = (END - max(d for d, _ in rows)).days if rows else 999
        if (s.frequency_30d, s.avg_session_min, s.recency_days) != (exp_freq, exp_avg, exp_rec):
            bad.append(s.player_id)
    assert not bad, f"{len(bad)} 名玩家快照会话特征对不上，如 {bad[:5]}"


def test_snapshot_defaults_for_unsampled_players(db):  # noqa: F811
    """口径落地检查：有消费无会话样本的玩家应 monetary>0 且 frequency=0；
    从未活跃的玩家 recency 应为 999（而不是被填成某个假日期）"""
    snaps = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).all()
    assert any(s.monetary_30d > 0 and s.frequency_30d == 0 for s in snaps), \
        "应存在有消费但无会话样本的玩家（付费全量 vs 会话样本两种口径并存）"
    assert any(s.recency_days == 999 and s.frequency_30d == 0 for s in snaps), \
        "应存在从未活跃（无会话）的玩家，recency=999"


def test_snapshot_run_dates_coexist(db):  # noqa: F811
    """设计规矩：快照按 run_date 版本化，不覆盖历史。补跑一个旧日期后两期应共存且行数一致。"""
    n_end = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).count()
    past = END - timedelta(days=7)
    res = run_feature_snapshot(db, past)
    n_past = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == past).count()
    n_end2 = db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == END).count()
    assert res["players"] == n_past == n_end == n_end2


def _check_funnel(db, game):  # noqa: F811
    out = funnel(game=game, days=30, db=db)
    assert "error" not in out
    vals = [s["count"] for s in out["steps"]]
    assert vals[0] == out["new_players"] > 0, "第一步人数应等于窗口内新玩家数"
    assert all(vals[i] >= vals[i + 1] for i in range(5)), f"{game} 漏斗不单调 {vals}"
    for s in out["steps"]:
        assert abs(s["pct"] - round(s["count"] / vals[0] * 100, 1)) < 0.11
    bd = out["biggest_drop"]
    assert bd["from"] == STEP_NAMES[2] and bd["to"] == STEP_NAMES[3], \
        f"{game} 最大流失点应在序章→第 4 关，实际 {bd['from']}→{bd['to']}"
    assert bd["count"] == vals[2] - vals[3]
    chan_new = sum(c["new"] for c in out["channels"])
    assert chan_new == out["new_players"], f"{game} 渠道新增合计 {chan_new} ≠ 新玩家 {out['new_players']}"
    for c in out["channels"]:
        assert 0 <= c["completion"] <= 100
        if c["d1_sample"] is not None and c["tracked"] >= 30:
            assert 35 <= c["d1_sample"] <= 75, \
                f"{game}/{c['name']} 次日回访 {c['d1_sample']}% 超出合理带（0% 恒零 bug 与 90% 小样本噪声都出现过）"
    cmp_ = out["compare"]
    assert abs(cmp_["delta_pt"] - round(cmp_["now"] - cmp_["prev"], 1)) < 0.11, "两期对比差值不自洽"
    return out


def test_funnel_endpoint_logic_gi(db):  # noqa: F811
    _check_funnel(db, "gi")


def test_funnel_endpoint_logic_hsr(db):  # noqa: F811
    _check_funnel(db, "hsr")
