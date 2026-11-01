"""分析接口（阶段 2 起）：总览页的数据全部来自数据库聚合，不再用前端假数。"""
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.core import (DimGame, DimPlayer, DimVersion, DimBanner, FactDailyMetric,
                            FactPayment, FactRetentionCohort, FactFeedback)

router = APIRouter(tags=["analytics"])
TIER_LABEL = {"free": "零氪", "minnow": "月卡党", "dolphin": "中R", "whale": "大R"}


def _game(db: Session, code: str) -> DimGame:
    return db.query(DimGame).filter(DimGame.code == code).first()


@router.get("/analytics/overview")
def overview(game: str = Query("gi"), db: Session = Depends(get_db)):
    g = _game(db, game)
    if not g:
        return {"error": "game not found"}
    metrics = (db.query(FactDailyMetric).filter(FactDailyMetric.game_id == g.id)
               .order_by(FactDailyMetric.metric_date.desc()).limit(30).all())
    metrics.reverse()
    if not metrics:
        return {"error": "no data"}
    today, yday = metrics[-1], metrics[-2] if len(metrics) > 1 else metrics[-1]

    def pct(cur, prev):
        return round((cur - prev) / prev * 100, 1) if prev else 0.0

    d1_latest = (db.query(FactRetentionCohort).filter(FactRetentionCohort.game_id == g.id)
                 .order_by(FactRetentionCohort.cohort_week.desc()).first())
    d1_prev = (db.query(FactRetentionCohort).filter(FactRetentionCohort.game_id == g.id)
               .order_by(FactRetentionCohort.cohort_week.desc()).offset(1).first())
    kpis = [
        {"label": "今日活跃玩家", "value": f"{today.dau:,}", "delta": f"{pct(today.dau, yday.dau):+g}%",
         "up": today.dau >= yday.dau, "note": "数据截止 " + str(today.metric_date)},
        {"label": "新增玩家", "value": f"{today.new_users:,}", "delta": f"{pct(today.new_users, yday.new_users):+g}%",
         "up": today.new_users >= yday.new_users, "note": "注册即算新增"},
        {"label": "今日流水", "value": f"¥{today.revenue:,.0f}", "delta": f"{pct(today.revenue, yday.revenue):+g}%",
         "up": today.revenue >= yday.revenue, "note": f"付费玩家 {today.pay_users:,} 人"},
        {"label": "次日留存", "value": f"{(d1_latest.d1 * 100 if d1_latest else 0):.1f}%",
         "delta": f"{round((d1_latest.d1 - d1_prev.d1) * 100, 1) if d1_latest and d1_prev else 0:+g}pt",
         "up": bool(d1_latest and d1_prev and d1_latest.d1 >= d1_prev.d1), "note": "最新一期注册队列"},
    ]
    trend = {"days": [m.metric_date.strftime("%m/%d") for m in metrics],
             "dau": [m.dau for m in metrics],
             "revenue_wan": [round(m.revenue / 10000, 1) for m in metrics]}
    banner_rows = (db.query(DimBanner.name, func.sum(FactPayment.amount))
                   .join(FactPayment, FactPayment.banner_id == DimBanner.id)
                   .filter(DimBanner.game_id == g.id).group_by(DimBanner.name)
                   .order_by(func.sum(FactPayment.amount).desc()).limit(5).all())
    banner_top = [{"name": n, "amount_wan": round(a / 10000, 1)} for n, a in banner_rows]
    mix_rows = db.query(DimPlayer.payer_tier, func.count(DimPlayer.id)).filter(
        DimPlayer.game_id == g.id).group_by(DimPlayer.payer_tier).all()
    mix = [{"name": TIER_LABEL.get(t, t), "value": c} for t, c in mix_rows]
    cohorts = (db.query(FactRetentionCohort).filter(
        FactRetentionCohort.game_id == g.id,
        FactRetentionCohort.cohort_week <= today.metric_date - timedelta(days=7))  # d7 可观测的队列才上图
        .order_by(FactRetentionCohort.cohort_week.desc()).limit(4).all())
    cohorts.reverse()
    retention = {"weeks": [c.cohort_week.strftime("%m/%d") + " 期" for c in cohorts],
                 "d1": [round(c.d1 * 100, 1) for c in cohorts],
                 "d7": [round(c.d7 * 100, 1) for c in cohorts]}
    ver = (db.query(DimVersion).filter(DimVersion.game_id == g.id)
           .order_by(DimVersion.start_date.desc()).first())
    ver_days = (today.metric_date - ver.start_date).days + 1 if ver else 0
    fb_yday = db.query(FactFeedback).filter(FactFeedback.game_id == g.id,
                                            FactFeedback.fb_date == today.metric_date - timedelta(days=1)).count()
    feed = []
    if ver:
        feed.append({"tag": "版本", "cls": "b-purple",
                     "text": f"{ver.code} 版本「{ver.title}」开启第 {ver_days} 天，今日活跃 {today.dau:,} 人", "time": "今天"})
    if banner_top:
        feed.append({"tag": "卡池", "cls": "b-blue",
                     "text": f"卡池「{banner_top[0]['name']}」累计收入居版本首位（¥{banner_top[0]['amount_wan']} 万）", "time": "今天"})
    feed.append({"tag": "反馈", "cls": "b-amber",
                 "text": f"昨日新增版本反馈 {fb_yday:,} 条，可在版本反馈页查看方面分布", "time": "昨天"})
    if d1_latest and d1_prev:
        d = round((d1_latest.d1 - d1_prev.d1) * 100, 1)
        feed.append({"tag": "留存", "cls": "b-green" if d >= 0 else "b-red",
                     "text": f"最新注册队列次日留存 {d1_latest.d1 * 100:.1f}%，较上期 {d:+g}pt", "time": "昨天"})
    return {"game": game, "kpis": kpis, "trend": trend, "banner_top": banner_top,
            "mix": mix, "retention": retention, "feed": feed, "as_of": str(today.metric_date)}
