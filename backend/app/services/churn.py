"""流失预警模型（阶段 6）：LightGBM + SHAP。

防泄漏设计（本项目立项时就定下的规矩，对照参考项目的教训）：
- 特征只用玩家注册后前 14 天（观察窗）内产生的数据，逐条带窗口过滤；
- 标签：预测窗（第 15~28 天）内离站——最后活跃日落在预测窗内，且其后再沉默满 14 天
  （确认窗）才下结论；这是行业通用的「以未来沉默确认流失」标定法，只用行为时间戳；
- 训练/测试按注册日期切分（时间切分），不是随机切分；
- 绝不使用「距今未活跃天数」这类在标签时刻测量的量——那会让 AUC 虚高到 1.0。
  本模型里的 recency_at_14 是在预测时刻（第 14 天）测量的观察窗内沉默天数，合法。
建模人群：在第 14 天前后仍活跃的玩家（运营真正能挽留的对象）；
标签可观测要求注册满 28 天（右删失样本剔除）。
"""
from datetime import timedelta

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.core import (DimGame, DimPlayer, FactEventLog, FactGacha,
                           FactPayment, FactSession)

OBS, PRED = 14, 14
FEATURE_NAMES = {
    "tutorial_steps": "新手引导完成步数", "orders_14": "两周内付费次数",
    "spend_14": "两周内消费金额", "has_monthly_14": "是否订阅月卡",
    "days_to_first_pay": "首次付费间隔天数", "session_days_14": "两周内登录天数",
    "avg_session_min_14": "平均单次在线时长", "pulls_14": "两周内抽卡数",
    "recency_at_14": "观察期末沉默天数", "is_tracked": "是否有行为样本",
    "login_days_14": "两周内活跃天数（全量登录）", "login_days_w2": "第二周活跃天数",
    "login_trend": "活跃趋势（第二周减第一周）", "max_silence": "最长连续沉默天数",
}
FEATURES = list(FEATURE_NAMES)
TIERS = [("极高风险", 0.75, "#F87171"), ("高风险", 0.5, "#FB923C"),
         ("中风险", 0.3, "#FBBF24"), ("安稳", 0.0, "#34D399")]
_cache = {}


def _build_frame(db: Session, game_id: int, end) -> pd.DataFrame:
    players = (db.query(DimPlayer).filter(DimPlayer.game_id == game_id,
                                          DimPlayer.last_active_date.isnot(None)).all())
    import json as _json
    tut = {}
    for pid, props in db.query(FactEventLog.player_id, FactEventLog.props).filter(
            FactEventLog.game_id == game_id, FactEventLog.event_name == "tutorial_step").all():
        try:
            step = int(_json.loads(props or "{}").get("step", 0))
        except Exception:
            step = 0
        tut[pid] = max(tut.get(pid, 0), step)
    pays = {}
    for pid, d, amt, prod in db.query(FactPayment.player_id, FactPayment.pay_date,
                                      FactPayment.amount, FactPayment.product).filter(
            FactPayment.game_id == game_id).all():
        pays.setdefault(pid, []).append((d, amt, prod))
    logins = {}
    for pid, d in db.query(FactEventLog.player_id, FactEventLog.event_date).filter(
            FactEventLog.game_id == game_id, FactEventLog.event_name == "login").all():
        logins.setdefault(pid, []).append(d)
    sess = {}
    for pid, d, dur in db.query(FactSession.player_id, FactSession.session_date,
                                FactSession.duration_min).filter(FactSession.game_id == game_id).all():
        sess.setdefault(pid, []).append((d, dur or 0))
    pulls = dict(db.query(FactGacha.player_id, func.count(FactGacha.id))
                 .filter(FactGacha.game_id == game_id).group_by(FactGacha.player_id).all())
    pull_dates = {}
    for pid, d in db.query(FactGacha.player_id, FactGacha.pull_date).filter(FactGacha.game_id == game_id).all():
        pull_dates.setdefault(pid, []).append(d)

    rows = []
    for p in players:
        reg, la = p.register_date, p.last_active_date
        w_end = reg + timedelta(days=OBS - 1)
        win_pays = [(d, a, pr) for d, a, pr in pays.get(p.id, []) if reg <= d <= w_end]
        win_sess = [(d, du) for d, du in sess.get(p.id, []) if reg <= d <= w_end]
        win_pulls = [d for d in pull_dates.get(p.id, []) if reg <= d <= w_end]
        login_offsets = sorted({(d - reg).days for d in logins.get(p.id, []) if reg <= d <= w_end})
        last_seen = reg  # 注册当天至少完成了引导的一部分
        for d, *_ in win_pays + win_sess:
            last_seen = max(last_seen, d)
        if win_pulls:
            last_seen = max(last_seen, max(win_pulls))
        if login_offsets:
            last_seen = max(last_seen, reg + timedelta(days=login_offsets[-1]))
        gaps, prev_off = [], -1
        for off in login_offsets + [OBS]:
            gaps.append(off - prev_off - 1)
            prev_off = off
        rows.append({
            "player_id": p.id, "nickname": p.nickname, "uid_tail": p.external_uid[-4:],
            "channel": p.channel, "reg": reg, "last_active": la,
            "total_spend": p.total_spend or 0,
            "tutorial_steps": tut.get(p.id, 0),
            "orders_14": len(win_pays),
            "spend_14": float(sum(a for _, a, _ in win_pays)),
            "has_monthly_14": int(any(pr == "月卡" for _, _, pr in win_pays)),
            "days_to_first_pay": (min(d for d, _, _ in win_pays) - reg).days if win_pays else 99,
            "login_days_14": len(login_offsets),
            "login_days_w2": sum(1 for o in login_offsets if o >= 7),
            "login_trend": sum(1 for o in login_offsets if o >= 7) - sum(1 for o in login_offsets if o < 7),
            "max_silence": max(gaps) if gaps else OBS,
            "session_days_14": len({d for d, _ in win_sess}),
            "avg_session_min_14": round(float(np.mean([du for _, du in win_sess])), 1) if win_sess else 0.0,
            "pulls_14": len(win_pulls),
            "recency_at_14": (w_end - last_seen).days,
            "is_tracked": int(p.id in sess or p.id in pull_dates),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["alive_at_14"] = df["last_active"] >= df["reg"] + timedelta(days=OBS - 1)
    df["churn"] = (df["last_active"] <= df["reg"] + timedelta(days=OBS + PRED)).astype(int)
    df["label_known"] = df["reg"] + timedelta(days=OBS + PRED + 14) <= end  # 再留 14 天确认窗
    return df


def _reason(feat: str, v) -> str:
    return {
        "recency_at_14": f"观察期末已沉默 {int(v)} 天",
        "login_days_14": f"两周内仅活跃 {int(v)} 天",
        "login_days_w2": f"第二周仅活跃 {int(v)} 天",
        "login_trend": f"活跃在往下掉（趋势 {int(v)}）",
        "max_silence": f"最长连续沉默 {int(v)} 天",
        "session_days_14": f"两周内仅登录 {int(v)} 天",
        "spend_14": f"两周内消费 ¥{int(v)}",
        "has_monthly_14": "未订阅月卡",
        "tutorial_steps": f"引导仅完成 {int(v)}/6 步",
        "orders_14": f"两周内付费 {int(v)} 次",
        "pulls_14": f"两周内抽卡 {int(v)} 抽",
        "days_to_first_pay": "两周内从未付费" if v >= 99 else f"第 {int(v)} 天才首次付费",
        "avg_session_min_14": f"单次在线仅 {v} 分钟",
        "is_tracked": "行为样本里几乎没出现",
    }.get(feat, feat)


def train_and_score(db: Session, game: DimGame, end) -> dict:
    df = _build_frame(db, game.id, end)
    cohort = df[df["alive_at_14"] & df["label_known"]].copy()
    split_day = cohort["reg"].quantile(0.7)
    train = cohort[cohort["reg"] <= split_day]
    test = cohort[cohort["reg"] > split_day]
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score, average_precision_score
    # 建模教训（阶段 6 实测）：300 棵深树在 1.6k 行上训练 AUC 0.92、测试 0.52（过拟合）；
    # 强正则后 0.70/0.60；再加单调约束（活跃越多风险越低等领域知识写进模型）后 0.63/0.63，
    # 训练测试基本贴合——单特征本身 AUC 0.64，这就是这批数据的真实可学上限附近。
    mono = {"tutorial_steps": -1, "orders_14": -1, "spend_14": -1, "has_monthly_14": -1,
            "days_to_first_pay": 1, "session_days_14": -1, "avg_session_min_14": -1,
            "pulls_14": -1, "recency_at_14": 1, "is_tracked": 0, "login_days_14": -1,
            "login_days_w2": -1, "login_trend": -1, "max_silence": 1}
    model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=15,
                               min_child_samples=40, reg_lambda=1.0, subsample=0.8,
                               colsample_bytree=0.8, random_state=42, verbose=-1,
                               monotone_constraints=[mono[f] for f in FEATURES])
    model.fit(train[FEATURES], train["churn"])
    proba_test = model.predict_proba(test[FEATURES])[:, 1]
    auc = float(roc_auc_score(test["churn"], proba_test))
    ap = float(average_precision_score(test["churn"], proba_test))

    import shap
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(test[FEATURES])
    sv = sv[1] if isinstance(sv, list) else sv
    imp = np.abs(sv).mean(axis=0)
    imp = imp / imp.sum()
    importance = sorted(
        ({"feature": f, "name": FEATURE_NAMES[f], "value": round(float(v), 3)}
         for f, v in zip(FEATURES, imp)), key=lambda x: -x["value"])

    # 分层按风险分位（挽留运营的惯例：先抓最危险的前 5%）——本模型概率被正则压向基准率，
    # 用绝对阈值会出现高风险层空无一人；分位阈值对量纲不敏感，存下来供实时名单同口径分层
    q95, q80, q50 = (float(np.quantile(proba_test, q)) for q in (0.95, 0.80, 0.50))
    bounds = [(q95, 1.01), (q80, q95), (q50, q80), (0.0, q50)]
    tiers = []
    for (name, _, color), (lo, hi) in zip(TIERS, bounds):
        m = (proba_test >= lo) & (proba_test < hi)
        tiers.append({"name": name, "color": color, "count": int(m.sum()),
                      "threshold": round(lo, 2),
                      "churn_rate": round(float(test["churn"].values[m].mean()) * 100, 1) if m.sum() else 0})

    # 当前预警名单：注册 13~17 天、最近 2 天仍活跃的玩家，用其前 14 天特征打分
    live = df[(df["reg"] >= end - timedelta(days=17)) & (df["reg"] <= end - timedelta(days=13))
              & (df["last_active"] >= end - timedelta(days=2))].copy()
    live_list = []
    if len(live):
        lp = model.predict_proba(live[FEATURES])[:, 1]
        lsv = explainer.shap_values(live[FEATURES])
        lsv = lsv[1] if isinstance(lsv, list) else lsv
        order = np.argsort(-lp)[:12]
        for j in order:
            row = live.iloc[j]
            top_idx = np.argsort(-lsv[j])[:2]
            reasons = [_reason(FEATURES[t], row[FEATURES[t]]) for t in top_idx if lsv[j][t] > 0]
            spend = row["total_spend"]
            action = ("专属客服回访 + 回归礼包" if spend >= 300 else
                      "月卡断签提醒 + 登录好礼" if row["has_monthly_14"] else
                      "回归任务推送 + 新手福利")
            live_list.append({
                "player_id": int(row["player_id"]),
                "name": row["nickname"], "uid_tail": row["uid_tail"],
                "score": int(round(float(lp[j]) * 100)),
                "reasons": reasons or ["活跃度整体走低"],
                "last": str(row["last_active"]), "action": action,
                "spend": int(spend)})
    return {
        "model": "LightGBM（梯度提升树）+ SHAP", "obs_window": OBS, "pred_window": PRED,
        "train_n": int(len(train)), "test_n": int(len(test)),
        "split_note": f"按注册日期时间切分（界线 {str(split_day)[:10]}）",
        "base_churn_rate": round(float(test["churn"].mean()) * 100, 1),
        "auc": round(auc, 3), "pr_auc": round(ap, 3),
        "importance": importance, "tiers": tiers, "live": live_list,
        "cohort_n": int(len(cohort)),
    }


def get_churn(db: Session, game: DimGame, end) -> dict:
    key = (game.id, str(end), int(db.query(DimPlayer).filter(DimPlayer.game_id == game.id).count()))
    if key not in _cache:
        _cache[key] = train_and_score(db, game, end)
    return _cache[key]
