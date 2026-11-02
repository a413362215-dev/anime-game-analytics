"""玩家分群（阶段 5）：RFM 五分位打分 + 规则标签（主） / K-Means（交叉验证）。

RFM 口径（本系统数据窗口与来源构成下的定义，页面上有标注）：
- R 近度 = 快照 recency_days（来自玩家维度 last_active_date，全量）
- F 频次 = 近 30 天会话天数（样本口径） + 近 30 天付费次数（全量），记为综合活跃频次
- M 金额 = 180 天窗口内累计消费 total_spend（全量）。注意不用五分位：月卡 ¥30 的定价让
  消费额高度离散（大量玩家恰好 ¥30/¥60），分位切点会压在同一个值上——阶段 5 实测
  M=3 一度只剩「恰好花了 60 元」的 63 人。改用行业常用的绝对金额带分档。
打分：按全量玩家的 20/40/60/80 分位切点给 1~5 分（R 反向）。
标签：8 类互斥规则，按顺序首命中（沉睡优先于价值，避免把已流失的大佬算成现役大佬）。
K-Means：对 [log 近度, F, log 消费] 标准化后 k=4、固定种子，结果只作交叉参照：
若规则分群与算法聚类大体重合，说明分组不是拍脑袋。
"""
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.core import DimPlayer, FactPayment, FactGacha, PlayerFeatureSnapshot

SEGMENTS = [
    # key, 名称, 徽标色, 描述, 运营建议（列表顺序 = 页面展示顺序，与判定顺序无关）
    ("whale", "氪金大佬", "b-amber", "出手阔绰，新卡池首日必到场", "新角色提前透出，专属客服跟进"),
    ("mid_r", "稳定中R", "b-purple", "每月预算固定，理性消费", "礼包性价比要算得清清楚楚"),
    ("monthly", "月卡党", "b-blue", "细水长流，月卡从不断供", "月卡福利别缩水，断签提醒要温柔"),
    ("grinder", "肝帝", "b-green", "在线时长拉满，体力永远不够", "给足挑战内容，他们是社区的火种"),
    ("at_risk", "流失预警", "b-amber", "曾经活跃或付费，正在变凉", "在彻底离站前发回归任务与福利"),
    ("newbie", "萌新玩家", "b-green", "刚上车不足一月，还在认路", "引导别催，首抽体验要顺滑"),
    ("swing", "摇摆玩家", "b-amber", "来去随心，活动好就回来", "用回归活动和热点话题拉他们一把"),
    ("sleeper", "沉睡玩家", "b-red", "已 30 天以上没有回来，多半已经离站", "大版本节点发召回，附专属回归礼"),
]
# 说明：原设计的「收藏党」（每个卡池都抽）在这批数据里不存在——抽卡行为是
# 「冲五星 or 抽个四星」的二值形态（实测全服抽数 ≥80 的 24 人全是 大佬/已沉睡），
# 故以可真实判定的「流失预警」替代，与歪率同理，不编造人群。
SEG_MAP = {s[0]: s for s in SEGMENTS}
_cache = {}


def _score(values: np.ndarray, reverse: bool) -> np.ndarray:
    """五分位打分 1~5；reverse=True 时值越小分越高（R）。并列时同分。"""
    cuts = np.percentile(values, [20, 40, 60, 80])
    idx = np.searchsorted(cuts, values, side="left")  # 0..4
    return (5 - idx) if reverse else (idx + 1)


def _score_sparse(values: np.ndarray) -> np.ndarray:
    """零膨胀维度的打分（F/M 专用）：全量五分位会把切点压进 0 附近，
    花 90 元买月卡的人会被打成 M=5「大佬」——阶段 5 实测踩到。
    改为：值为 0 → 1 分；非零部分内部按四分位给 2~5 分。"""
    out = np.ones(len(values), dtype=int)
    nz = values > 0
    if nz.sum() >= 4:
        cuts = np.percentile(values[nz], [25, 50, 75])
        out[nz] = np.searchsorted(cuts, values[nz], side="left") + 2
    return out


def _m_tier(spend: float) -> int:
    """M 金额带：0 未付费 / 1 ≤60 / 2 ≤300 / 3 ≤1000 / 4 >1000（180 天累计消费）。"""
    if spend <= 0:
        return 0
    if spend <= 60:
        return 1
    if spend <= 300:
        return 2
    if spend <= 1000:
        return 3
    return 4


def _classify(r, f, m_tier, *, recency, has_monthly, reg_age_days):
    # 判定顺序即优先级：先流失侧（沉睡→预警），再价值侧（大佬→订阅→中R），最后行为与兜底
    if recency > 30:
        return "sleeper"
    if 15 <= recency <= 30 and (m_tier >= 2 or f >= 4):
        return "at_risk"
    if m_tier == 4:
        return "whale"
    if has_monthly:
        return "monthly"
    if m_tier in (2, 3) and f >= 2:
        return "mid_r"
    if f >= 4:
        return "grinder"
    if reg_age_days <= 30:
        return "newbie"
    return "swing"


def compute_segments(db: Session, game_id: int, run_date) -> dict:
    snaps = (db.query(PlayerFeatureSnapshot)
             .filter(PlayerFeatureSnapshot.game_id == game_id,
                     PlayerFeatureSnapshot.run_date == run_date).all())
    players = {p.id: p for p in db.query(DimPlayer).filter(DimPlayer.game_id == game_id).all()}
    from datetime import timedelta as _td
    monthly_ids = {pid for (pid,) in db.query(FactPayment.player_id).filter(
        FactPayment.game_id == game_id, FactPayment.product == "月卡",
        FactPayment.pay_date >= run_date - _td(days=35)).all()}
    pulls_map, banner_map = {}, {}
    for pid, n, nb in (db.query(FactGacha.player_id, func.count(FactGacha.id),
                                func.count(func.distinct(FactGacha.banner_id)))
                       .filter(FactGacha.game_id == game_id).group_by(FactGacha.player_id).all()):
        pulls_map[pid] = n; banner_map[pid] = nb

    rec = np.array([min(s.recency_days, 180) for s in snaps], dtype=float)
    frq = np.array([s.frequency_30d + s.orders_30d for s in snaps], dtype=float)
    mon = np.array([players[s.player_id].total_spend or 0 for s in snaps], dtype=float)
    rs, fs, ms = _score(rec, True), _score_sparse(frq), _score_sparse(mon)

    labels = []
    for i, s in enumerate(snaps):
        p = players[s.player_id]
        labels.append(_classify(int(rs[i]), int(fs[i]), _m_tier(float(mon[i])),
                                recency=s.recency_days,
                                has_monthly=s.player_id in monthly_ids,
                                reg_age_days=(run_date - p.register_date).days))
    total = len(snaps)
    groups = []
    for key, name, cls, desc, advice in SEGMENTS:
        idx = [i for i, l in enumerate(labels) if l == key]
        if not idx:
            continue
        seg_players = [players[snaps[i].player_id] for i in idx]
        payers = sum(1 for p in seg_players if (p.total_spend or 0) > 0)
        groups.append({
            "key": key, "name": name, "cls": cls, "desc": desc, "advice": advice,
            "count": len(idx), "share": round(len(idx) / total * 100, 1),
            "pay_rate": round(payers / len(idx) * 100),
            "avg_spend": round(float(mon[idx].mean())),
            "avg_monetary_30d": round(float(np.mean([snaps[i].monetary_30d for i in idx]))),
            "avg_freq": round(float(frq[idx].mean()), 1),
        })

    # 散点采样：每玩家 [近度(=180-近度天数), F, 累计消费]，按组分系列
    rng = np.random.default_rng(7)
    scatter = {}
    order = rng.permutation(total)
    taken = 0
    for i in order:
        if taken >= 420:
            break
        k = labels[i]
        scatter.setdefault(k, []).append([int(180 - rec[i]), int(frq[i]), int(mon[i])])
        taken += 1

    # K-Means 交叉验证
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    X = np.column_stack([np.log1p(rec), frq, np.log1p(mon)])
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=4, random_state=42, n_init=10).fit(Xs)
    sil = float(silhouette_score(Xs, km.labels_, sample_size=min(2000, total),
                                 random_state=42)) if total > 4 else 0.0
    centers = []
    for c in range(4):
        m_ = km.labels_ == c
        centers.append({"count": int(m_.sum()),
                        "avg_spend": round(float(mon[m_].mean())),
                        "avg_recency": round(float(rec[m_].mean()), 1),
                        "avg_freq": round(float(frq[m_].mean()), 1)})
    order_c = sorted(range(4), key=lambda c: -centers[c]["avg_spend"])
    names_c = ["高价值簇", "均衡簇", "活跃簇", "沉睡簇"]
    # 按平均近度给剩余簇命名：近度最小（最久未归）的叫沉睡簇
    named = {}
    named[order_c[0]] = names_c[0]
    rest = [c for c in range(4) if c != order_c[0]]
    rest.sort(key=lambda c: -centers[c]["avg_recency"])
    named[rest[0]] = "沉睡簇"
    rest2 = [c for c in rest[1:]]
    rest2.sort(key=lambda c: -centers[c]["avg_freq"])
    named[rest2[0]] = "活跃簇"
    named[rest2[1]] = "均衡簇"
    clusters = [{"name": named[c], **centers[c]} for c in range(4)]

    return {"run_date": str(run_date), "total": total, "groups": groups,
            "scatter": {SEG_MAP[k][1]: v for k, v in scatter.items()},
            "kmeans": {"k": 4, "silhouette": round(sil, 3), "clusters": clusters},
            "_labels": labels, "_snaps": snaps}


def get_segments(db: Session, game_id: int) -> dict:
    run_date = (db.query(func.max(PlayerFeatureSnapshot.run_date))
                .filter(PlayerFeatureSnapshot.game_id == game_id).scalar())
    n = db.query(PlayerFeatureSnapshot).filter(
        PlayerFeatureSnapshot.game_id == game_id,
        PlayerFeatureSnapshot.run_date == run_date).count()
    key = (game_id, str(run_date), n)
    if key not in _cache:
        out = compute_segments(db, game_id, run_date)
        out.pop("_labels", None); out.pop("_snaps", None)
        _cache[key] = out
    return _cache[key]
