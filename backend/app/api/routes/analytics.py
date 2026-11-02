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


STEP_NAMES = ["首次启动", "创建角色", "完成序章引导", "通关第 4 关", "完成首抽", "进入主线章节"]
CHANNEL_LABEL = {"official": "官方渠道", "bilibili": "Bilibili", "taptap": "TapTap", "ios": "应用商店", "import": "导入"}


@router.get("/analytics/funnel")
def funnel(game: str = Query("gi"), days: int = Query(30), db: Session = Depends(get_db)):
    """新手漏斗：窗口内注册的新玩家，各教程步的到达人数（fact_event_log 口径）。
    渠道次日回访为被追踪样本口径（fact_session），已在返回里标注样本量。"""
    import json as _json
    from ...models.core import FactEventLog, FactSession
    g = _game(db, game)
    if not g:
        return {"error": "game not found"}
    end = db.query(func.max(FactDailyMetric.metric_date)).filter(FactDailyMetric.game_id == g.id).scalar()

    def window_steps(win_start, win_end):
        pids = [pid for (pid,) in db.query(DimPlayer.id).filter(
            DimPlayer.game_id == g.id, DimPlayer.register_date >= win_start,
            DimPlayer.register_date <= win_end).all()]
        counts = {i: 0 for i in range(1, 7)}
        if pids:
            rows = (db.query(FactEventLog.props, func.count(func.distinct(FactEventLog.player_id)))
                    .filter(FactEventLog.event_name == "tutorial_step",
                            FactEventLog.player_id.in_(pids)).group_by(FactEventLog.props).all())
            for props, c in rows:
                counts[_json.loads(props)["step"]] = c
        return [counts[i] for i in range(1, 7)], len(pids)

    start = end - timedelta(days=days - 1)
    vals, n_new = window_steps(start, end)
    steps = []
    for i, v in enumerate(vals):
        steps.append({"name": STEP_NAMES[i], "count": v,
                      "pct": round(v / vals[0] * 100, 1) if vals[0] else 0,
                      "conv": round(vals[i + 1] / v * 100, 1) if i < 5 and v else None,
                      "drop": (v - vals[i + 1]) if i < 5 else 0})
    drops = [(steps[i]["drop"], i) for i in range(5)]
    bd = max(drops) if drops else (0, 0)
    biggest = {"from": STEP_NAMES[bd[1]], "to": STEP_NAMES[bd[1] + 1], "count": bd[0],
               "share": round(bd[0] / vals[0] * 100, 1) if vals[0] else 0}
    prev_vals, _ = window_steps(end - timedelta(days=2 * days - 1), start - timedelta(days=1))
    conv_now = round(vals[5] / vals[0] * 100, 1) if vals[0] else 0
    conv_prev = round(prev_vals[5] / prev_vals[0] * 100, 1) if prev_vals[0] else 0

    # 渠道：新增（全量）/ 引导完成率（全量）/ 次日回访（被追踪样本）
    channels = []
    chan_rows = db.query(DimPlayer.channel, func.count(DimPlayer.id)).filter(
        DimPlayer.game_id == g.id, DimPlayer.register_date >= start).group_by(DimPlayer.channel).all()
    for ch, cnt in sorted(chan_rows, key=lambda x: -x[1]):
        if ch == "import":
            continue
        pids = [pid for (pid,) in db.query(DimPlayer.id).filter(
            DimPlayer.game_id == g.id, DimPlayer.channel == ch, DimPlayer.register_date >= start).all()]
        reached = {1: 0, 6: 0}
        if pids:
            for props, c in (db.query(FactEventLog.props, func.count(func.distinct(FactEventLog.player_id)))
                             .filter(FactEventLog.event_name == "tutorial_step",
                                     FactEventLog.player_id.in_(pids)).group_by(FactEventLog.props).all()):
                step = _json.loads(props)["step"]
                if step in reached:
                    reached[step] = c
        # 次日回访用全期被追踪样本（30 日窗口每渠道仅 10~20 人，噪声太大）；
        # 在 Python 侧算：SQLite 里 date 列 + timedelta 的 SQL 表达式不可靠（实测恒为 0）
        all_pids = [pid for (pid,) in db.query(DimPlayer.id).filter(
            DimPlayer.game_id == g.id, DimPlayer.channel == ch).all()]
        reg_map = dict(db.query(DimPlayer.id, DimPlayer.register_date).filter(
            DimPlayer.id.in_(all_pids)).all())
        sess = {}
        for pid2, sd in db.query(FactSession.player_id, FactSession.session_date).filter(
                FactSession.player_id.in_(all_pids)).all():
            sess.setdefault(pid2, set()).add(sd)
        tracked = len(sess)
        d1_back = sum(1 for pid2, rd in reg_map.items()
                      if pid2 in sess and rd + timedelta(days=1) in sess[pid2])
        channels.append({"name": CHANNEL_LABEL.get(ch, ch), "new": cnt,
                         "completion": round(reached[6] / reached[1] * 100, 1) if reached[1] else 0,
                         "d1_sample": round(d1_back / tracked * 100, 1) if tracked else None,
                         "tracked": tracked})
    return {"game": game, "days": days, "new_players": n_new, "steps": steps,
            "biggest_drop": biggest, "channels": channels,
            "compare": {"now": conv_now, "prev": conv_prev, "delta_pt": round(conv_now - conv_prev, 1)}}


@router.get("/analytics/gacha")
def gacha(game: str = Query("gi"), db: Session = Depends(get_db)):
    """付费与抽卡：口径全部来自 fact_gacha / fact_payment。
    说明：抽卡流水为「导入 + 被追踪样本」口径（与真实来源构成一致）；
    歪率需要 UP/非 UP 物品标记，本系统物品维度暂无该标记，故第四个 KPI 用深保底占比代替，不编造歪率。"""
    from ...models.core import FactGacha, DimItem
    g = _game(db, game)
    if not g:
        return {"error": "game not found"}
    ver = (db.query(DimVersion).filter(DimVersion.game_id == g.id)
           .order_by(DimVersion.start_date.desc()).first())
    # 统计口径：全期（180 天）。当前版本仅 12 天、五星样本约 30 个，直方图与均值噪声过大；
    # 等版本数据攒够再切版本口径。页面文案已按全期标注。
    win = db.query(FactGacha).filter(FactGacha.game_id == g.id)
    total = win.count()
    five_rows = win.filter(FactGacha.rarity == 5).all()
    five = len(five_rows)
    pities = sorted(r.pity_count for r in five_rows)
    avg_pity = round(sum(pities) / five, 1) if five else 0
    median_pity = pities[five // 2] if five else 0
    deep_share = round(sum(1 for p in pities if p >= 80) / five * 100, 1) if five else 0
    buckets = [f"{i * 10 + 1}-{i * 10 + 10}" for i in range(9)]
    hist = [0] * 9
    for p in pities:
        hist[min((p - 1) // 10, 8)] += 1
    kpis = [
        {"label": "累计总抽数", "value": f"{total:,}", "note": "近 180 天 · 导入+追踪样本口径"},
        {"label": "五星出货率", "value": f"{(five / total * 100 if total else 0):.2f}%", "note": "含保底 · 基础 0.6% + 软保底"},
        {"label": "平均出货抽数", "value": f"{avg_pity} 抽", "note": f"中位数 {median_pity} 抽"},
        {"label": "深保底占比", "value": f"{deep_share}%", "note": "80 抽之后才出货的五星占比"},
    ]
    pool_rows = (db.query(DimBanner.name, func.count(FactGacha.id))
                 .join(FactGacha, FactGacha.banner_id == DimBanner.id)
                 .filter(DimBanner.game_id == g.id).group_by(DimBanner.name)
                 .order_by(func.count(FactGacha.id).desc()).limit(5).all())
    pools = [{"name": n, "pulls": c} for n, c in pool_rows]
    top_ids = (db.query(FactGacha.player_id, func.count(FactGacha.id).label("n"))
               .filter(FactGacha.game_id == g.id).group_by(FactGacha.player_id)
               .order_by(func.count(FactGacha.id).desc()).limit(5).all())
    tops = []
    for pid, pulls in top_ids:
        p = db.query(DimPlayer).get(pid)
        spend = db.query(func.coalesce(func.sum(FactPayment.amount), 0)).filter(
            FactPayment.player_id == pid).scalar()
        p5 = [r.pity_count for r in db.query(FactGacha).filter(
            FactGacha.player_id == pid, FactGacha.rarity == 5).all()]
        fav = (db.query(DimBanner.name, func.count(FactGacha.id))
               .join(FactGacha, FactGacha.banner_id == DimBanner.id)
               .filter(FactGacha.player_id == pid).group_by(DimBanner.name)
               .order_by(func.count(FactGacha.id).desc()).first())
        tops.append({"name": p.nickname, "uid_tail": p.external_uid[-4:], "pulls": pulls,
                     "spend": round(spend), "five": len(p5),
                     "avg_pity": round(sum(p5) / len(p5)) if p5 else 0,
                     "pool": fav[0] if fav else "—"})
    return {"game": game, "version": {"code": ver.code, "title": ver.title},
            "kpis": kpis, "hist": {"buckets": buckets, "counts": hist},
            "pools": pools, "tops": tops}


@router.get("/analytics/segments")
def segments(game: str = Query("gi"), db: Session = Depends(get_db)):
    from ...services.segmentation import get_segments
    g = _game(db, game)
    if not g:
        return {"error": "game not found"}
    out = get_segments(db, g.id)
    return {"game": game, **out}


@router.get("/analytics/churn")
def churn(game: str = Query("gi"), db: Session = Depends(get_db)):
    from ...services.churn import get_churn
    from ...services.datagen import END as DATA_END
    g = _game(db, game)
    if not g:
        return {"error": "game not found"}
    out = get_churn(db, g, DATA_END)
    # 名单附上阶段 5 的分群标签（同一名玩家在两个模型里对得上号）
    try:
        from ...services.segmentation import compute_segments, SEG_MAP
        from ...models.core import PlayerFeatureSnapshot
        rd = db.query(func.max(PlayerFeatureSnapshot.run_date)).filter(
            PlayerFeatureSnapshot.game_id == g.id).scalar()
        seg = compute_segments(db, g.id, rd)
        id2seg = {sn.player_id: SEG_MAP[l][1] for sn, l in zip(seg["_snaps"], seg["_labels"])}
        for row in out["live"]:
            row["segment"] = id2seg.get(row.get("player_id"), "—")
    except Exception:
        for row in out["live"]:
            row["segment"] = "—"
    high = sum(t["count"] for t in out["tiers"] if t["name"] in ("极高风险", "高风险"))
    mid = next(t["count"] for t in out["tiers"] if t["name"] == "中风险")
    top_tier = out["tiers"][0]
    kpis = [
        {"label": "高风险玩家（测试集）", "value": f"{high:,}", "note": "未来 14 天大概率离站"},
        {"label": "中风险玩家（测试集）", "value": f"{mid:,}", "note": "活跃正在下滑，先观察"},
        {"label": "模型 AUC（时间切分测试）", "value": f"{out['auc']}", "note": f"PR-AUC {out['pr_auc']} · 基准流失率 {out['base_churn_rate']}%"},
        {"label": "极高风险组实际流失率", "value": f"{top_tier['churn_rate']}%", "note": "分层校准：分数越高、流失越真"},
    ]
    return {"game": game, "kpis": kpis, **out}
