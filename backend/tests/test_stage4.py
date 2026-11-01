"""阶段 4 验证：抽卡接口口径——分布合计、概率/均值重算、大佬榜逐项对账。"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy import func  # noqa: E402
from app.models.core import DimBanner, FactGacha, FactPayment  # noqa: E402
from app.api.routes.analytics import gacha  # noqa: E402


def _check(db, game):  # noqa: F811
    from app.models.core import DimGame
    out = gacha(game=game, db=db)
    assert "error" not in out
    gid = db.query(DimGame).filter(DimGame.code == game).first().id
    total = db.query(FactGacha).filter(FactGacha.game_id == gid).count()
    five = db.query(FactGacha).filter(FactGacha.game_id == gid,
                                      FactGacha.rarity == 5).all()
    # 分布合计 == 五星总数；每桶与独立重算一致
    assert sum(out["hist"]["counts"]) == len(five)
    pities = [r.pity_count for r in five]
    for i, c in enumerate(out["hist"]["counts"]):
        expect = sum(1 for p in pities if i * 10 + 1 <= p <= i * 10 + 10)
        assert c == expect, f"{game} 第 {i} 桶 {c} != {expect}"
    # KPI 与重算一致
    k = {x["label"]: x["value"] for x in out["kpis"]}
    assert k["累计总抽数"] == f"{total:,}"
    assert abs(float(k["五星出货率"].rstrip("%")) - round(len(five) / total * 100, 2)) < 0.011
    assert abs(float(k["平均出货抽数"].split()[0]) - round(sum(pities) / len(pities), 1)) < 0.051
    # 软保底形态：71-80 桶应是分布峰值（生成规则的指纹，防口径回归）
    assert out["hist"]["counts"][7] == max(out["hist"]["counts"])
    # 卡池：逐池与 group-by 重算一致
    for pool in out["pools"]:
        real = (db.query(func.count(FactGacha.id)).join(DimBanner, DimBanner.id == FactGacha.banner_id)
                .filter(DimBanner.name == pool["name"]).scalar())
        assert pool["pulls"] == real
    # 大佬榜：按抽数降序；逐人五星数/消费与流水对账
    pulls_seq = [t["pulls"] for t in out["tops"]]
    assert pulls_seq == sorted(pulls_seq, reverse=True)
    from app.models.core import DimPlayer
    for t in out["tops"]:
        p = db.query(DimPlayer).filter(DimPlayer.game_id == gid, DimPlayer.nickname == t["name"],
                                       DimPlayer.external_uid.like(f"%{t['uid_tail']}")).first()
        assert p is not None
        real_pulls = db.query(FactGacha).filter(FactGacha.player_id == p.id).count()
        real_five = db.query(FactGacha).filter(FactGacha.player_id == p.id, FactGacha.rarity == 5).count()
        real_spend = db.query(func.coalesce(func.sum(FactPayment.amount), 0)).filter(
            FactPayment.player_id == p.id).scalar()
        assert (t["pulls"], t["five"], t["spend"]) == (real_pulls, real_five, round(real_spend))


def test_gacha_endpoint_gi(db):  # noqa: F811
    _check(db, "gi")


def test_gacha_endpoint_hsr(db):  # noqa: F811
    _check(db, "hsr")
