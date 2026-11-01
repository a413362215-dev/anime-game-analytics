"""模拟数据生成器（阶段 2）：确定性随机（seed 固定），生成两款游戏 180 天的完整数据。

诚实声明：这是为开发与演示合成的数据，不是任何游戏的真实运营数据；
页面上会以「模拟数据」徽标明示。生成逻辑尽量贴近真实规律：
- 留存按注册天数衰减、版本更新日与周末有抬升
- 抽卡严格走保底规则（五星基础 0.6%，74 抽起软保底，90 抽硬保底）
- 日指标、留存队列、特征快照都由同一份行为模拟汇总，与事实表互相自洽
只有约 10% 的「被追踪玩家」生成逐条抽卡/登录流水（对应现实里从 UIGF 等渠道导入的样本），
其余玩家只贡献聚合指标——这与真实数据来源的构成一致。
"""
import hashlib
import random
from datetime import date, timedelta, datetime, time as dtime

from sqlalchemy.orm import Session

from ..models.core import (DataSource, SyncTask, DimGame, DimVersion, DimBanner, DimItem,
                           DimPlayer, FactEventLog, FactSession, FactPayment, FactGacha,
                           FactFeedback, FactDailyMetric, FactRetentionCohort,
                           PlayerFeatureSnapshot)

END = date(2026, 11, 1)
START = END - timedelta(days=179)
SEED = 20261101

GAMES = [
    {"code": "gi", "name": "原神", "players": 4200,
     "versions": [("4.7", "云堇试弦"), ("4.8", "蔷薇与绮梦"), ("5.0", "流灰之径"), ("5.1", "织夜巡礼"), ("5.2", "流光拾遗之旅")],
     "banners": ["月下拾光", "星海巡航", "花间四杰", "云间候月", "风起鹤归", "烟火之邀", "深渊咏唱", "苍雷紫电"],
     "chars5": ["拾光", "澜溪", "烬羽"], "chars4": ["小满", "阿萝", "铁牛", "青黛", "sorrel"]},
    {"code": "hsr", "name": "崩坏：星穹铁道", "players": 3100,
     "versions": [("3.3", "银河驿站"), ("3.4", "雾桥来信"), ("3.5", "群星低语"), ("3.6", "霜原回声"), ("3.7", "穿越银河")],
     "banners": ["穿越银河", "星间漫游", "击鼓催花", "霜刃试弦", "雾桥来信", "长夜灯塔"],
     "chars5": ["巡星", "弥娅", "玄铠"], "chars4": ["点点", "鸦九", "白芷", "砾"]},
]
PRODUCTS = [(6, "6 元首充"), (30, "月卡"), (68, "68 档直购"), (128, "128 档直购"), (328, "328 档直购"), (648, "648 档直购")]
TIER_W = [("free", .54), ("minnow", .24), ("dolphin", .15), ("whale", .07)]
CHANNELS = [("official", .46), ("bilibili", .22), ("taptap", .14), ("ios", .18)]
ASPECTS = ["剧情", "角色", "美术音乐", "玩法", "优化卡顿", "抽卡福利"]
FB_TEMPLATES = {
    "剧情": [("这次主线写得真好，最后一段直接看哭了", .9, 5), ("剧情节奏有点拖，中间睡着了两次", -.3, 3), ("新地图的支线比主线还有意思", .6, 4)],
    "角色": [("新角色建模太顶了，手感也顺滑", .9, 5), ("命座设计有点恶心，零命残缺感强", -.6, 2), ("待机动作好可爱，抽到就是胜利", .8, 5)],
    "美术音乐": [("新场景美到截图当壁纸，音乐一起鸡皮疙瘩", 1.0, 5), ("配乐还是稳定发挥，探索不无聊", .6, 4), ("这次 PV 剪辑一般，没什么记忆点", -.2, 3)],
    "玩法": [("新活动玩法有新意，和朋友联机很欢乐", .7, 4), ("深渊环境又针对老角色了，无语", -.5, 2), ("日常减负好评，五分钟清完", .8, 5)],
    "优化卡顿": [("更新完狂掉帧，手机发烫严重", -.9, 1), ("这次优化不错，老机型也流畅了", .7, 4), ("加载时间变长了，进图等半天", -.6, 2), ("闪退两次了，补偿赶紧发", -.8, 1)],
    "抽卡福利": [("70 抽双黄！这版本我原地封神", 1.0, 5), ("小保底又歪，常驻角色都满命了", -.7, 2), ("送的十连很良心，希望保持", .7, 4), ("池子排期太密，钱包顶不住", -.4, 3)],
}


def _pick(rng, weighted):
    x, acc = rng.random(), 0.0
    for v, w in weighted:
        acc += w
        if x <= acc:
            return v
    return weighted[-1][0]


def _flush(db: Session, model, rows, chunk=4000):
    for i in range(0, len(rows), chunk):
        db.bulk_insert_mappings(model, rows[i:i + chunk])
    rows.clear()


def generate(db: Session) -> dict:
    if db.query(DimGame).count() > 0:
        return {"skipped": True}
    rng = random.Random(SEED)
    days = [START + timedelta(days=i) for i in range(180)]
    summary = {}

    # ---- 数据源（与数据管理页的卡片一一对应 + 一个生成器来源） ----
    src_defs = [
        ("uigf", "原神 · 抽卡记录 (UIGF)", "file", "ready", "从游戏祈愿历史导出的标准格式文件，一键入库"),
        ("srgf", "星穹铁道 · 抽卡记录 (SRGF)", "file", "ready", "跃迁记录的标准导出格式，字段自动映射"),
        ("enka", "Enka · 角色展柜", "api", "connected", "凭 UID 读取公开的角色展柜，补全角色与圣遗物"),
        ("hoyolab", "HoYoLAB / 米游社", "api", "connected", "经 genshin.py 读取账号公开数据与社区帖子"),
        ("feedback_csv", "评论与反馈文件", "file", "ready", "TapTap / B站 / 应用商店评论导出的 CSV、Excel"),
        ("custom", "自定义数据源", "api", "pending", "REST 接口或数据库直连，自己写一个适配器即可"),
        ("simulator", "模拟数据生成器", "manual", "connected", "本地合成的演示数据（本系统当前的数据来源）"),
    ]
    sources = {}
    for code, name, kind, status, desc in src_defs:
        s = DataSource(code=code, name=name, kind=kind, status=status, description=desc)
        db.add(s); db.flush(); sources[code] = s.id

    for g in GAMES:
        gr = random.Random(SEED + (11 if g["code"] == "gi" else 77))  # 不能用 hash()：字符串哈希每进程随机，会破坏确定性
        game = DimGame(code=g["code"], name=g["name"]); db.add(game); db.flush()
        gid = game.id

        # ---- 版本与卡池 ----
        versions = []
        for vi, (vcode, vtitle) in enumerate(g["versions"]):
            vs = START + timedelta(days=vi * 42)
            ve = vs + timedelta(days=41) if vi < 4 else END
            v = DimVersion(game_id=gid, code=vcode, title=vtitle, start_date=vs, end_date=ve)
            db.add(v); db.flush(); versions.append(v)
        banners = []
        std = DimBanner(game_id=gid, version_id=None, name="常驻祈愿" if g["code"] == "gi" else "群星跃迁",
                        banner_type="standard", start_date=START, end_date=END)
        db.add(std); db.flush(); banners.append(std)
        bi = 0
        for v in versions:
            for half in (0, 1):
                bs = v.start_date + timedelta(days=half * 21)
                if bs > v.end_date:
                    continue  # 版本不足整 42 天（如数据截止日截断）时不生成越界卡池
                be = min(bs + timedelta(days=20), v.end_date)
                b = DimBanner(game_id=gid, version_id=v.id, name=g["banners"][bi % len(g["banners"])],
                              banner_type="character", start_date=bs, end_date=be)
                db.add(b); db.flush(); banners.append(b); bi += 1
        char_banners = [b for b in banners if b.banner_type == "character"]

        # ---- 物品 ----
        items = []
        for ci, nm in enumerate(g["chars5"]):
            it = DimItem(game_id=gid, external_item_id=f"15{ci:02d}", name=nm, item_type="character", rarity=5)
            db.add(it); db.flush(); items.append(it)
        for ci, nm in enumerate(g["chars4"]):
            it = DimItem(game_id=gid, external_item_id=f"14{ci:02d}", name=nm, item_type="character", rarity=4)
            db.add(it); db.flush(); items.append(it)
        wp = DimItem(game_id=gid, external_item_id="13001", name="试作武器", item_type="weapon", rarity=3)
        db.add(wp); db.flush(); items.append(wp)
        item5, item4, item3 = items[:3], items[3:-1], items[-1]

        # ---- 玩家注册分布：版本首日有尖峰 ----
        reg_days = []
        for d in days:
            w = 1.0 + (2.6 if d in [v.start_date for v in versions] else 0) + (0.35 if d.weekday() >= 5 else 0)
            reg_days.append(w)
        tot_w = sum(reg_days)
        players = []
        for pi in range(g["players"]):
            x, acc, reg = gr.random() * tot_w, 0.0, days[-1]
            for d, w in zip(days, reg_days):
                acc += w
                if x <= acc:
                    reg = d; break
            tier = _pick(gr, TIER_W)
            players.append({
                "game_id": gid, "external_uid": f"{880000000 + pi * 7 + gr.randint(0, 5)}",
                "nickname": f"旅人{pi:04d}", "channel": _pick(gr, CHANNELS),
                "register_date": reg, "level": 1, "payer_tier": tier,
                "total_spend": 0.0, "last_active_date": None, "_tier": tier, "_reg": reg,
                "_active_days": [], "_spend": 0.0, "_pulls30": 0, "_sess": [],
            })
        db.bulk_insert_mappings(DimPlayer, [{k: v for k, v in p.items() if not k.startswith("_")} for p in players])
        db.flush()
        db_players = db.query(DimPlayer).filter(DimPlayer.game_id == gid).order_by(DimPlayer.id).all()
        for p, row in zip(players, db_players):
            p["_id"] = row.id
        tracked = set(gr.sample(range(len(players)), k=max(60, len(players) // 10)))
        gacha_src = sources["uigf"] if g["code"] == "gi" else sources["srgf"]

        events, sessions, payments, gachas, feedbacks = [], [], [], [], []
        pull_seq = 0  # external_id 专用单调计数，不能用 len(列表)：列表会被 _flush 清空
        pay_seq = 0
        daily = {}
        version_start_set = {v.start_date for v in versions}
        pity = {i: 0 for i in tracked}
        for d in days:
            is_ver = d in version_start_set
            wknd = 1.18 if d.weekday() >= 5 else 1.0
            dau = new_u = pay_u = 0
            rev = 0.0
            cur_banner = next((b for b in char_banners if b.start_date <= d <= b.end_date), char_banners[-1])
            for pi, p in enumerate(players):
                if p["_reg"] > d:
                    continue
                age = (d - p["_reg"]).days
                if p["_reg"] == d:
                    new_u += 1
                    # 新手漏斗：注册当天走教程，逐步流失（第 4 关掉得最多，和漏斗页口径一致）
                    step_p = [1.0, .86, .74, .58, .52, .47]
                    reach = 1.0
                    for si, sp in enumerate(step_p):
                        reach = sp
                        if gr.random() < sp / (step_p[si - 1] if si else 1.0) or si == 0:
                            events.append({"game_id": gid, "player_id": p["_id"], "source_id": sources["simulator"],
                                           "event_name": "tutorial_step", "event_date": d,
                                           "event_time": datetime.combine(d, dtime(10, si * 7 % 50)), "props": f'{{"step": {si + 1}}}'})
                        else:
                            break
                base = 0.38 * (0.5 ** (age / 30)) + 0.13           # 留存衰减 + 长尾（次日≈50%）
                if is_ver:
                    base *= 1.45
                base *= wknd
                if p["_tier"] in ("dolphin", "whale"):
                    base *= 1.35
                if gr.random() > min(base, .93):
                    continue
                dau += 1
                p["_active_days"].append(d)
                p["last_active_date"] = d
                dur = round(gr.lognormvariate(3.4, .7), 1)
                p["_sess"].append(dur)
                if pi in tracked:
                    events.append({"game_id": gid, "player_id": p["_id"], "source_id": sources["simulator"],
                                   "event_name": "login", "event_date": d,
                                   "event_time": datetime.combine(d, dtime(gr.randint(7, 23), gr.randint(0, 59))), "props": ""})
                    sessions.append({"game_id": gid, "player_id": p["_id"], "session_date": d,
                                     "duration_min": dur, "source_id": sources["simulator"]})
                # ---- 付费 ----
                tier = p["_tier"]
                pay_amt = 0.0
                if tier == "minnow" and age % 30 == 1:
                    pay_amt, prod = 30, "月卡"
                elif tier == "dolphin" and gr.random() < (0.16 if d in [cur_banner.start_date + timedelta(days=i) for i in range(3)] else 0.045):
                    pay_amt, prod = _pick(gr, [((68, "68 档直购"), .4), ((128, "128 档直购"), .35), ((328, "328 档直购"), .25)])
                elif tier == "whale" and gr.random() < (0.30 if d == cur_banner.start_date else 0.07):
                    pay_amt, prod = _pick(gr, [((328, "328 档直购"), .45), ((648, "648 档直购"), .4), ((128, "128 档直购"), .15)])
                if pay_amt:
                    pay_u += 1; rev += pay_amt; p["_spend"] += pay_amt
                    payments.append({"game_id": gid, "player_id": p["_id"],
                                     "banner_id": cur_banner.id if tier != "minnow" else None,
                                     "source_id": sources["simulator"], "external_id": f"sim-{g['code']}-{pay_seq}",
                                     "amount": pay_amt, "product": prod,
                                     "paid_at": datetime.combine(d, dtime(gr.randint(8, 23), gr.randint(0, 59))), "pay_date": d})
                    pay_seq += 1
                # ---- 抽卡（仅被追踪玩家逐条记） ----
                if pi in tracked:
                    pull_p = {"free": .05, "minnow": .10, "dolphin": .30, "whale": .55}[tier]
                    if d == cur_banner.start_date:
                        pull_p = min(pull_p * 2.2, .95)
                    if gr.random() < pull_p:
                        n = gr.randint(1, 10) if tier != "whale" else gr.randint(10, 40)
                        if (END - d).days <= 30:
                            p["_pulls30"] += n
                        for _ in range(n):
                            pity[pi] += 1
                            pc = pity[pi]
                            rate = 0.006 if pc < 74 else min(0.006 + (pc - 73) * 0.06, 1.0)
                            if gr.random() < rate:
                                rarity, it = 5, gr.choice(item5); pity[pi] = 0
                            elif pc % 10 == 0 or gr.random() < 0.051:
                                rarity, it = 4, gr.choice(item4)
                            else:
                                rarity, it = 3, item3
                            gachas.append({"game_id": gid, "player_id": p["_id"], "banner_id": cur_banner.id,
                                           "item_id": it.id, "source_id": gacha_src,
                                           "external_id": f"{g['code']}-{p['_id']}-{pull_seq}",
                                           "banner_type": "character", "rarity": rarity, "pity_count": pc,
                                           "pulled_at": datetime.combine(d, dtime(gr.randint(8, 23), gr.randint(0, 59))), "pull_date": d})
                            pull_seq += 1
            daily[d] = {"game_id": gid, "metric_date": d, "dau": dau, "new_users": new_u,
                        "revenue": round(rev, 2), "pay_users": pay_u, "sessions": dau}
            # ---- 反馈：版本首周量大；优化卡顿在版本首日有负面尖峰 ----
            n_fb = gr.randint(22, 40) + (26 if is_ver else 0)
            ver = next((v for v in versions if v.start_date <= d <= v.end_date), versions[-1])
            for fi in range(n_fb):
                asp = "优化卡顿" if (is_ver and gr.random() < .34) else gr.choice(ASPECTS)
                content, sent, rating = gr.choice(FB_TEMPLATES[asp])
                ts = datetime.combine(d, dtime(gr.randint(0, 23), gr.randint(0, 59)))
                feedbacks.append({"game_id": gid, "version_id": ver.id, "source_id": sources["feedback_csv"],
                                  "external_id": hashlib.md5(f"{g['code']}|{ts}|{fi}|{content}".encode()).hexdigest()[:24],
                                  "content": content, "rating": rating, "sentiment": sent,
                                  "aspect": asp, "created_at": ts, "fb_date": d})
            if len(events) > 20000: _flush(db, FactEventLog, events)
            if len(sessions) > 20000: _flush(db, FactSession, sessions)
            if len(payments) > 20000: _flush(db, FactPayment, payments)
            if len(gachas) > 20000: _flush(db, FactGacha, gachas)
            if len(feedbacks) > 20000: _flush(db, FactFeedback, feedbacks)
        _flush(db, FactEventLog, events); _flush(db, FactSession, sessions)
        _flush(db, FactPayment, payments); _flush(db, FactGacha, gachas); _flush(db, FactFeedback, feedbacks)
        _flush(db, FactDailyMetric, list(daily.values()))

        # ---- 玩家回写等级与累计消费 ----
        for p in players:
            p["total_spend"] = round(p["_spend"], 2)
            p["level"] = min(60, 8 + len(p["_active_days"]) // 3)
        db.bulk_update_mappings(DimPlayer, [{"id": p["_id"], "total_spend": p["total_spend"],
                                             "level": p["level"], "last_active_date": p["last_active_date"]} for p in players])

        # ---- 留存队列（按注册周） ----
        cohorts = {}
        for p in players:
            monday = p["_reg"] - timedelta(days=p["_reg"].weekday())
            cohorts.setdefault(monday, []).append(p)
        rows = []
        for monday, ps in cohorts.items():
            def rate(k):
                ok = sum(1 for p in ps if p["_reg"] + timedelta(days=k) in set(p["_active_days"]))
                return round(ok / len(ps), 4) if ps else 0
            rows.append({"game_id": gid, "cohort_week": monday, "cohort_size": len(ps),
                         "d1": rate(1), "d7": rate(7), "d30": rate(30)})
        _flush(db, FactRetentionCohort, rows)

        # ---- 特征快照（run_date = 数据截止日） ----
        snaps = []
        for p in players:
            a30 = [d for d in p["_active_days"] if (END - d).days <= 30]
            snaps.append({"game_id": gid, "player_id": p["_id"], "run_date": END,
                          "recency_days": (END - p["last_active_date"]).days if p["last_active_date"] else 999,
                          "frequency_30d": len(a30), "monetary_30d": 0.0,
                          "avg_session_min": round(sum(p["_sess"]) / len(p["_sess"]), 1) if p["_sess"] else 0,
                          "level": p["level"], "gacha_pulls_30d": p["_pulls30"]})
        _flush(db, PlayerFeatureSnapshot, snaps)

        # ---- 来源计数回写 + 同步任务留痕 ----
        counts = {
            "uigf": db.query(FactGacha).filter(FactGacha.game_id == gid, FactGacha.source_id == sources["uigf"]).count() if g["code"] == "gi" else None,
            "srgf": db.query(FactGacha).filter(FactGacha.game_id == gid, FactGacha.source_id == sources["srgf"]).count() if g["code"] == "hsr" else None,
        }
        summary[g["code"]] = {"players": len(players), "payments": db.query(FactPayment).filter(FactPayment.game_id == gid).count(),
                              "gacha": db.query(FactGacha).filter(FactGacha.game_id == gid).count(),
                              "feedback": db.query(FactFeedback).filter(FactFeedback.game_id == gid).count(),
                              "events": db.query(FactEventLog).filter(FactEventLog.game_id == gid).count()}
        for code, cnt in counts.items():
            if cnt is not None:
                s = db.query(DataSource).get(sources[code]); s.total_rows = cnt; s.last_sync_at = datetime.combine(END, dtime(10, 24))
        fb_src = db.query(DataSource).get(sources["feedback_csv"])
        fb_src.total_rows = (fb_src.total_rows or 0) + summary[g["code"]]["feedback"]; fb_src.last_sync_at = datetime.combine(END, dtime(9, 58))
        sim_src = db.query(DataSource).get(sources["simulator"])
        sim_src.total_rows = (sim_src.total_rows or 0) + summary[g["code"]]["events"] + summary[g["code"]]["payments"]
        sim_src.last_sync_at = datetime.combine(END, dtime(11, 0))
        db.add(SyncTask(source_id=sources["simulator"], title=f"{g['name']} · 模拟数据生成（180 天）",
                        added_rows=sum(summary[g["code"]].values()), skipped_rows=0, status="success",
                        detail="seed=20261101 确定性生成"))
    db.commit()
    return summary
