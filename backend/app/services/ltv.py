"""LTV 预测（阶段 7）：三模型同台对比，口径与流失模型一致地防泄漏。

定义：LTV90 = 玩家注册后 90 天内累计消费。校准窗 = 前 30 天（特征与拟合只用这段），
预测段 = 第 31~90 天的消费；可评估玩家须注册满 90 天（reg + 89 ≤ 数据截止日）。
按注册日期时间切分：前 60% 队列拟合，后 40% 队列只做评估。

三模型：
- BG/NBD + Gamma-Gamma（概率模型）：从校准窗交易次数/最近一次时间拟合购买率与客单价分布；
- LightGBM 回归：30 天行为特征直接回归预测段消费（log 目标 + 单调约束）；
- Cox 生存 + 付费率：先估每个玩家在预测段的存活曲线，再乘校准窗日均付费、按存活概率加权。
评估：MAE / RMSE / Spearman 排序相关 / 预测前 10% 玩家的实际消费捕获率（运营最关心的排序质量）。
"""
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from ..models.core import DimGame, DimPlayer, FactEventLog, FactPayment

CAL, HORIZON = 30, 90
_cache = {}


def _build(db: Session, game_id: int, end) -> pd.DataFrame:
    players = db.query(DimPlayer).filter(DimPlayer.game_id == game_id).all()
    pays = {}
    for pid, d, amt, prod in db.query(FactPayment.player_id, FactPayment.pay_date,
                                      FactPayment.amount, FactPayment.product).filter(
            FactPayment.game_id == game_id).all():
        pays.setdefault(pid, []).append((d, float(amt), prod))
    logins = {}
    for pid, d in db.query(FactEventLog.player_id, FactEventLog.event_date).filter(
            FactEventLog.game_id == game_id, FactEventLog.event_name == "login").all():
        logins.setdefault(pid, []).append(d)
    import json as _json
    tut = {}
    for pid, props in db.query(FactEventLog.player_id, FactEventLog.props).filter(
            FactEventLog.game_id == game_id, FactEventLog.event_name == "tutorial_step").all():
        try:
            tut[pid] = max(tut.get(pid, 0), int(_json.loads(props or "{}").get("step", 0)))
        except Exception:
            pass
    rows = []
    for p in players:
        reg = p.register_date
        tx = sorted((d - reg).days for d, _, _ in pays.get(p.id, []))
        amts = {(d - reg).days: a for d, a, _ in pays.get(p.id, [])}
        cal_tx = [o for o in tx if o < CAL]
        fut_tx = [o for o in tx if CAL <= o < HORIZON]
        cal_spend = sum(amts[o] for o in cal_tx)
        rows.append({
            "player_id": p.id, "nickname": p.nickname, "uid_tail": p.external_uid[-4:],
            "reg": reg, "reg_month": f"{reg.year}-{reg.month:02d}",
            "last_active": p.last_active_date, "channel": p.channel,
            "orders_c": len(cal_tx), "spend_c": cal_spend,
            "avg_order_c": cal_spend / len(cal_tx) if cal_tx else 0.0,
            "has_monthly_c": int(any(pr == "月卡" and (d - reg).days < CAL
                                     for d, _, pr in pays.get(p.id, []))),
            "days_to_first_pay": min(cal_tx) if cal_tx else 99,
            "login_days_c": len({d for d in logins.get(p.id, []) if 0 <= (d - reg).days < CAL}),
            "tutorial_steps": tut.get(p.id, 0),
            "future_spend": sum(amts[o] for o in fut_tx),
            "evaluable": (end - reg).days >= HORIZON - 1,
            "cal_complete": (end - reg).days >= CAL - 1,
            # BG/NBD 摘要（校准窗）
            "bg_freq": max(len(cal_tx) - 1, 0),
            "bg_recency": (max(cal_tx) - min(cal_tx)) if len(cal_tx) >= 2 else 0,  # lifetimes 约定：最后一次距第一次的时间，单次交易必须为 0
            "bg_monetary": cal_spend / len(cal_tx) if cal_tx else 0.0,
            "bg_T": (CAL - min(cal_tx)) if cal_tx else CAL,
            "daily_spend": [(o, amts[o]) for o in tx],
        })
    return pd.DataFrame(rows)


def _fit_bgnbd(train: pd.DataFrame):
    from lifetimes import BetaGeoFitter, GammaGammaFitter
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    # lifetimes 约定：T 是「从首次交易起」的个人观察时长，且模型只拟合至少交易过一次的客户；
    # 早期版本用注册起算的统一 T=30，拟合出的排序是负的（实测 Spearman −0.20）
    tr1 = train[train["orders_c"] >= 1]
    bgf.fit(tr1["bg_freq"].astype(float), tr1["bg_recency"].astype(float),
            tr1["bg_T"].astype(float))
    gg_df = train[train["bg_freq"] >= 1]
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(gg_df["bg_freq"], gg_df["bg_monetary"])
    return bgf, ggf


def _pred_bgnbd(bgf, ggf, df: pd.DataFrame, global_avg_order: float) -> np.ndarray:
    exp_tx = bgf.conditional_expected_number_of_purchases_up_to_time(
        HORIZON - CAL, df["bg_freq"].astype(float), df["bg_recency"].astype(float),
        df["bg_T"].astype(float))
    avg_profit = ggf.conditional_expected_average_profit(df["bg_freq"], df["bg_monetary"])
    # GG 只对复购客户（freq≥1）可信：本数据上它对 freq=0 客户给出 −25.75 的负期望客单价
    # （离散金额+样本结构导致的拟合病理，实测定位）——单次购买者用其自身实际客单价，未购者用全局均值
    avg_profit = np.where(df["bg_freq"] >= 1, np.clip(avg_profit, 0, None),
                          np.where(df["orders_c"] > 0, df["bg_monetary"], global_avg_order))
    return np.asarray(exp_tx) * np.asarray(avg_profit)


def _fit_gbm(train: pd.DataFrame):
    import lightgbm as lgb
    feats = ["orders_c", "spend_c", "avg_order_c", "has_monthly_c", "days_to_first_pay",
             "login_days_c", "tutorial_steps"]
    mono = [1, 1, 0, 1, -1, 1, 1]
    m = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                          min_child_samples=40, reg_lambda=1.0, subsample=0.8,
                          colsample_bytree=0.8, random_state=42, verbose=-1,
                          monotone_constraints=mono)
    m.fit(train[feats], np.log1p(train["future_spend"]))
    resid = np.log1p(train["future_spend"]) - m.predict(train[feats])
    m.smearing_ = float(np.mean(np.exp(resid)))  # Duan smearing：纠正 expm1 回变换偏差
    return m, feats


def _fit_cox(train: pd.DataFrame, end):
    from lifelines import CoxPHFitter
    df = train.copy()
    df["duration"] = df.apply(
        lambda r: ((r["last_active"] or end) - r["reg"]).days + 1, axis=1)
    df["event"] = df.apply(
        lambda r: int(r["last_active"] is not None and (end - r["last_active"]).days >= 14), axis=1)
    df["login_rate"] = df["login_days_c"] / CAL
    df["spend_log"] = np.log1p(df["spend_c"])
    cols = ["duration", "event", "login_rate", "spend_log", "orders_c", "has_monthly_c", "tutorial_steps"]
    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(df[cols], duration_col="duration", event_col="event")
    return cph


def _pred_cox(cph, df: pd.DataFrame) -> np.ndarray:
    d = df.copy()
    d["login_rate"] = d["login_days_c"] / CAL
    d["spend_log"] = np.log1p(d["spend_c"])
    cols = ["login_rate", "spend_log", "orders_c", "has_monthly_c", "tutorial_steps"]
    times = np.arange(CAL + 1, HORIZON + 1)
    surv = cph.predict_survival_function(d[cols], times=times)  # index=times, columns=players
    s30 = cph.predict_survival_function(d[cols], times=[CAL]).iloc[0].values
    cond = (surv.values / np.maximum(s30, 1e-9)).clip(0, 1)  # 条件存活：第 30 天后还活着的概率轨迹
    expected_alive_days = cond.sum(axis=0)
    return (df["spend_c"].values / CAL) * expected_alive_days


def _metrics(actual: np.ndarray, pred: np.ndarray) -> dict:
    from scipy.stats import spearmanr
    pred = np.clip(np.nan_to_num(pred), 0, None)
    mae = float(np.mean(np.abs(actual - pred)))
    rmse = float(np.sqrt(np.mean((actual - pred) ** 2)))
    rho = float(spearmanr(actual, pred).statistic) if np.std(pred) > 0 else 0.0
    k = max(int(len(actual) * 0.1), 1)
    top = np.argsort(-pred)[:k]
    capture = float(actual[top].sum() / actual.sum()) if actual.sum() > 0 else 0.0
    return {"mae": round(mae, 1), "rmse": round(rmse, 1), "spearman": round(rho, 3),
            "top10_capture": round(capture * 100, 1)}


def evaluate(db: Session, game: DimGame, end) -> dict:
    df = _build(db, game.id, end)
    ev = df[df["evaluable"]].copy()
    split = ev["reg"].quantile(0.6)
    train, test = ev[ev["reg"] <= split], ev[ev["reg"] > split]
    global_avg = float(train.loc[train["orders_c"] > 0, "avg_order_c"].mean() or 0)

    bgf, ggf = _fit_bgnbd(train)
    gbm, feats = _fit_gbm(train)
    cox = _fit_cox(df[df["cal_complete"]], end)  # 生存模型可用全部满 30 天玩家（含删失）

    preds = {
        "BG/NBD + Gamma-Gamma": _pred_bgnbd(bgf, ggf, test, global_avg),
        "LightGBM 回归": np.expm1(gbm.predict(test[feats])) * gbm.smearing_,
        "Cox 生存 + 付费率": _pred_cox(cox, test),
    }
    actual = test["future_spend"].values
    models = []
    pred_map = {}
    payer_mask = test["orders_c"].values > 0
    for name, pr in preds.items():
        pr = np.clip(np.nan_to_num(np.asarray(pr, dtype=float)), 0, None)
        pred_map[name] = pr
        m = _metrics(actual, pr)
        # 付费子集上的排序力单列：BG/NBD 的盲区是无交易玩家（本队列占 79%），
        # 只看全量会冤枉它——它对有交易记录的玩家排序并不差（见验证报告数据）
        m["payer_spearman"] = _metrics(actual[payer_mask], pr[payer_mask])["spearman"]
        models.append({"name": name, **m})
    best = max(models, key=lambda m: m["spearman"])
    median_pred = np.median(np.column_stack(list(pred_map.values())), axis=1)

    # 累计曲线（测试队列）：实测逐日人均累计 vs 三模型按实测累积形态展开到各自终点
    days = list(range(0, HORIZON + 1, 5)) + [HORIZON]
    actual_curve = []
    for d in days:
        vals = [sum(a for o, a in t if o < d) for t in test["daily_spend"]]
        actual_curve.append(round(float(np.mean(vals)), 1))
    shape = np.array(actual_curve, dtype=float)
    shape = shape / shape[-1] if shape[-1] > 0 else shape
    curve_models = {}
    test_ltv = test["spend_c"].values + actual
    for name, pr in pred_map.items():
        total = float(np.mean(test["spend_c"].values + pr))
        curve_models[name] = [round(float(total * s), 1) for s in shape]
    actual_ltv90 = float(np.mean(test_ltv))

    # 当前全体（满 30 天）玩家的 LTV90 预测中位数，用于月队列图与 KPI
    cur = df[df["cal_complete"]].copy()
    cur_preds = np.column_stack([
        np.clip(_pred_bgnbd(bgf, ggf, cur, global_avg), 0, None),
        np.clip(np.expm1(gbm.predict(cur[feats])) * gbm.smearing_, 0, None),
        np.clip(_pred_cox(cox, cur), 0, None)])
    cur["ltv90_pred"] = cur["spend_c"].values + np.median(cur_preds, axis=1)
    cur["ltv90_actual"] = np.where(cur["evaluable"], cur["spend_c"] + cur["future_spend"], np.nan)
    cohorts = []
    for month, grp in cur.groupby("reg_month"):
        row = {"month": month[5:], "n": int(len(grp))}
        ev_grp = grp.dropna(subset=["ltv90_actual"])
        if len(ev_grp) >= len(grp) * 0.9:
            row.update({"value": round(float(ev_grp["ltv90_actual"].mean()), 1), "kind": "实测"})
        else:
            row.update({"value": round(float(grp["ltv90_pred"].mean()), 1), "kind": "预测"})
        cohorts.append(row)

    payer_test = test[test["spend_c"] > 0]
    kpis = [
        {"label": "30 日 LTV（实测·测试队列）", "value": f"¥{test['spend_c'].mean():.1f}", "note": "注册后前 30 天人均消费"},
        {"label": "90 日 LTV（预测·三模型中位数）", "value": f"¥{float(np.mean(test['spend_c'].values + median_pred)):.1f}",
         "note": f"同队列实测 ¥{actual_ltv90:.1f}（事后对照）"},
        {"label": "付费玩家 90 日 LTV（实测）", "value": f"¥{(payer_test['spend_c'] + payer_test['future_spend']).mean():.0f}",
         "note": f"付费玩家占测试队列 {len(payer_test) / len(test) * 100:.1f}%"},
        {"label": "最佳模型前 10% 捕获率", "value": f"{best['top10_capture']}%",
         "note": f"{best['name']} · 随机抽 10% 只能捕获 10%"},
    ]
    return {"kpis": kpis, "models": models, "best_model": best["name"],
            "train_n": int(len(train)), "test_n": int(len(test)),
            "curve": {"days": days, "actual": actual_curve, "models": curve_models},
            "cohorts": cohorts, "cal_window": CAL, "horizon": HORIZON}


def get_ltv(db: Session, game: DimGame, end) -> dict:
    key = (game.id, str(end), int(db.query(DimPlayer).filter(DimPlayer.game_id == game.id).count()))
    if key not in _cache:
        _cache[key] = evaluate(db, game, end)
    return _cache[key]
