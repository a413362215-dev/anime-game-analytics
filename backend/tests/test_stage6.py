"""阶段 6 验证（流失模型）：防泄漏、窗口完整性、时间切分、AUC 合理带、分层校准、确定性。"""
import os, sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.models.core import DimGame, FactEventLog  # noqa: E402
from app.services.datagen import END  # noqa: E402
from app.services.churn import FEATURES, FEATURE_NAMES, _build_frame, train_and_score  # noqa: E402
from app.api.routes.analytics import churn as churn_route  # noqa: E402


def _game(db):  # noqa: F811
    return db.query(DimGame).filter(DimGame.code == "gi").first()


def test_no_leakage_features():
    """防泄漏红线：特征集合里不许出现任何用未来信息算的量。
    参考项目 AUC=1.0 的教训就来自 days_since_last_active（标签时刻测量）。"""
    banned = {"total_spend", "last_active", "last_active_date", "recency_days", "days_since_last_active"}
    assert not (set(FEATURES) & banned), f"特征里混入泄漏量：{set(FEATURES) & banned}"
    assert set(FEATURES) == set(FEATURE_NAMES), "特征与中文名映射必须一一对应"


def test_feature_window_integrity(db):  # noqa: F811
    """窗口完整性：抽 30 名玩家，login_days_14 必须等于其注册后 14 天内 login 事件天数（独立重算）"""
    g = _game(db)
    df = _build_frame(db, g.id, END)
    assert not df.empty
    sample = df.sample(30, random_state=1)
    for _, row in sample.iterrows():
        reg = row["reg"]
        days = {d for (d,) in db.query(FactEventLog.event_date).filter(
            FactEventLog.player_id == row["player_id"], FactEventLog.event_name == "login",
            FactEventLog.event_date >= reg, FactEventLog.event_date <= reg + timedelta(days=13)).all()}
        assert row["login_days_14"] == len(days), f"玩家 {row['player_id']} 活跃天数对不上"


def test_churn_model_metrics(db):  # noqa: F811
    """AUC 必须落在合理带：太低说明没学到东西，接近 1.0 说明泄漏——两个方向都算失败。
    分层校准单调：风险越高、实际流失率越高（允许相邻层相等）。"""
    out = train_and_score(db, _game(db), END)
    assert 0.58 < out["auc"] < 0.98, f"AUC {out['auc']} 超出合理带（低了没学到、高了是泄漏）"
    assert out["pr_auc"] > out["base_churn_rate"] / 100, "PR-AUC 应高于基准流失率（随机水平）"
    assert out["train_n"] + out["test_n"] == out["cohort_n"]
    rates = [t["churn_rate"] for t in out["tiers"]]
    assert all(rates[i] >= rates[i + 1] - 0.01 for i in range(3)), f"分层校准不单调：{rates}"
    assert sum(t["count"] for t in out["tiers"]) == out["test_n"]
    imp = [i["value"] for i in out["importance"]]
    assert imp == sorted(imp, reverse=True) and abs(sum(imp) - 1) < 0.02


def test_churn_deterministic(db):  # noqa: F811
    a = train_and_score(db, _game(db), END)
    b = train_and_score(db, _game(db), END)
    assert a["auc"] == b["auc"] and a["tiers"] == b["tiers"]


def test_churn_route_live_list(db):  # noqa: F811
    out = churn_route(game="gi", db=db)
    assert "error" not in out and len(out["kpis"]) == 4
    scores = [p["score"] for p in out["live"]]
    assert scores == sorted(scores, reverse=True) and all(0 <= s <= 100 for s in scores)
    assert all(p["reasons"] and p["segment"] for p in out["live"]), "名单每人须有 SHAP 原因与分群标签"
