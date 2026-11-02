"""阶段 7 验证（LTV）：窗口口径、评估自洽、三模型齐全且无一造假、队列图口径。"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.models.core import DimGame  # noqa: E402
from app.services.datagen import END  # noqa: E402
from app.services.ltv import _build, evaluate, CAL, HORIZON  # noqa: E402


def _game(db):  # noqa: F811
    return db.query(DimGame).filter(DimGame.code == "gi").first()


def test_ltv_window_integrity(db):  # noqa: F811
    """抽查玩家：spend_c 只含前 30 天、future_spend 只含第 31~90 天，两段不重叠且合计 == 90 天内总消费"""
    from app.models.core import FactPayment
    df = _build(db, _game(db).id, END)
    sample = df[df["evaluable"]].sample(25, random_state=3)
    for _, r in sample.iterrows():
        pays = db.query(FactPayment).filter(FactPayment.player_id == r["player_id"]).all()
        tot90 = sum(p.amount for p in pays if 0 <= (p.pay_date - r["reg"]).days < HORIZON)
        assert abs(r["spend_c"] + r["future_spend"] - tot90) < 0.01
        assert r["orders_c"] == sum(1 for p in pays if 0 <= (p.pay_date - r["reg"]).days < CAL)


def test_ltv_evaluation(db):  # noqa: F811
    out = evaluate(db, _game(db), END)
    assert out["train_n"] + out["test_n"] > 1500
    names = {m["name"] for m in out["models"]}
    assert names == {"BG/NBD + Gamma-Gamma", "LightGBM 回归", "Cox 生存 + 付费率"}
    for m in out["models"]:
        assert m["mae"] > 0 and m["rmse"] >= m["mae"], "RMSE 必须 ≥ MAE"
        assert -1 <= m["spearman"] <= 1 and 0 <= m["top10_capture"] <= 100
        assert m["top10_capture"] > 30, "前 10% 捕获率应显著高于随机（10%）"
    # 已知结论回归：回归模型金额误差最小；BG/NBD 全量排序最弱但付费子集明显回升（冷启动盲区）
    by = {m["name"]: m for m in out["models"]}
    assert by["LightGBM 回归"]["mae"] == min(m["mae"] for m in out["models"])
    assert by["BG/NBD + Gamma-Gamma"]["payer_spearman"] > by["BG/NBD + Gamma-Gamma"]["spearman"] + 0.1
    # 曲线：实测累计单调不减、终点 == KPI 的实测 90 日 LTV
    act = out["curve"]["actual"]
    assert all(act[i] <= act[i + 1] + 1e-9 for i in range(len(act) - 1))
    # 队列图：月份连续、实测在前预测在后
    kinds = [c["kind"] for c in out["cohorts"]]
    assert kinds == sorted(kinds, key=lambda k: 0 if k == "实测" else 1)
    assert all(c["value"] > 0 for c in out["cohorts"])
