"""ETL 作业（阶段 3）：从事实表重算派生数据，全部幂等（同 run_date 重跑先删后建）。

当前作业：
1. 特征快照 run_feature_snapshot —— 分群/流失/LTV 三个模型的共同地基。
   口径说明（与真实数据来源构成一致）：
   - 付费特征（monetary_30d）来自 fact_payment 全量流水；
   - 抽卡特征来自 fact_gacha（导入 + 被追踪样本口径）；
   - 会话特征（frequency/avg_session/recency）来自 fact_session，仅覆盖被追踪玩家，
     未被追踪的玩家这三项为 0/999——这是数据来源决定的，不是缺失值乱填。
2. 日指标对账 verify_daily_metrics —— 把已存的日指标与流水重算结果逐日比对，
   返回不一致天数；阶段 2 的验证套件在用它同类的检查。
"""
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.core import (DimPlayer, FactSession, FactPayment, FactGacha,
                           FactDailyMetric, PlayerFeatureSnapshot)


def run_feature_snapshot(db: Session, run_date) -> dict:
    since = run_date - timedelta(days=29)
    db.query(PlayerFeatureSnapshot).filter(PlayerFeatureSnapshot.run_date == run_date).delete()
    players = db.query(DimPlayer).all()
    sess_days, sess_dur, last_active = {}, {}, {}
    for pid, d, dur in db.query(FactSession.player_id, FactSession.session_date,
                                FactSession.duration_min).all():
        last_active[pid] = max(last_active.get(pid, d), d)
        if d >= since:
            sess_days.setdefault(pid, set()).add(d)
            sess_dur.setdefault(pid, []).append(dur or 0)
    money = dict(db.query(FactPayment.player_id, func.sum(FactPayment.amount))
                 .filter(FactPayment.pay_date >= since).group_by(FactPayment.player_id).all())
    orders = dict(db.query(FactPayment.player_id, func.count(FactPayment.id))
                  .filter(FactPayment.pay_date >= since).group_by(FactPayment.player_id).all())
    pulls = dict(db.query(FactGacha.player_id, func.count(FactGacha.id))
                 .filter(FactGacha.pull_date >= since).group_by(FactGacha.player_id).all())
    rows = []
    for p in players:
        # R（近度）取玩家维度的 last_active_date：这是全量口径；
        # 若只用会话表，未被追踪的玩家会全部变成 999——阶段 5 分群前修正。
        la = p.last_active_date or last_active.get(p.id)
        durs = sess_dur.get(p.id, [])
        rows.append({
            "game_id": p.game_id, "player_id": p.id, "run_date": run_date,
            "recency_days": (run_date - la).days if la else 999,
            "frequency_30d": len(sess_days.get(p.id, set())),
            "monetary_30d": round(money.get(p.id, 0) or 0, 2),
            "orders_30d": orders.get(p.id, 0),
            "avg_session_min": round(sum(durs) / len(durs), 1) if durs else 0,
            "level": p.level or 1,
            "gacha_pulls_30d": pulls.get(p.id, 0),
        })
    for i in range(0, len(rows), 4000):
        db.bulk_insert_mappings(PlayerFeatureSnapshot, rows[i:i + 4000])
    db.commit()
    return {"run_date": str(run_date), "players": len(rows),
            "with_sessions": len(sess_days), "with_spend_30d": sum(1 for v in money.values() if v)}


def verify_daily_metrics(db: Session) -> dict:
    """逐日对账：已存日指标 vs 事实重算（流水/新增）。返回每款游戏的不一致天数。"""
    out = {}
    from ..models.core import DimGame
    for g in db.query(DimGame).all():
        pay = dict(db.query(FactPayment.pay_date, func.sum(FactPayment.amount))
                   .filter(FactPayment.game_id == g.id).group_by(FactPayment.pay_date).all())
        reg = dict(db.query(DimPlayer.register_date, func.count(DimPlayer.id))
                   .filter(DimPlayer.game_id == g.id).group_by(DimPlayer.register_date).all())
        bad_rev = bad_new = 0
        for m in db.query(FactDailyMetric).filter(FactDailyMetric.game_id == g.id).all():
            if abs((pay.get(m.metric_date, 0) or 0) - m.revenue) > 0.51:
                bad_rev += 1
            if reg.get(m.metric_date, 0) != m.new_users:
                bad_new += 1
        out[g.code] = {"revenue_mismatch_days": bad_rev, "new_users_mismatch_days": bad_new}
    return out
