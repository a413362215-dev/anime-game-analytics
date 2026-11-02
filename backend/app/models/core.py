"""核心数据模型（阶段 2 数据层）：30 表全量设计的前三层 16 张先落地。

分层约定（与设计定版一致）：
- 系统层：谁在用系统、数据从哪来、同步跑了什么
- 维度层：游戏 / 玩家 / 版本 / 卡池 / 物品——事实表只挂外键，不重复存名字
- 事实层：事件、会话、付费、抽卡、反馈、日指标、留存队列
- 分析枢纽：player_feature_snapshot 提前建好，分群/流失/LTV 三个模型共用同一份特征
规矩：事实表带 game_id + source_id；可导入的事实带 external_id 唯一约束防重复入库。
"""
from sqlalchemy import (Column, Integer, String, Float, Date, DateTime, Text,
                        ForeignKey, UniqueConstraint, Index, func)
from ..db.session import Base


# ---------- 系统层 ----------
class DataSource(Base):
    __tablename__ = "data_source"
    id = Column(Integer, primary_key=True)
    code = Column(String(32), unique=True, nullable=False)      # uigf / srgf / enka / hoyolab / feedback_csv / custom
    name = Column(String(128), nullable=False)
    kind = Column(String(32), nullable=False, default="file")    # file / api / manual
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=True)
    status = Column(String(16), nullable=False, default="ready")  # ready / connected / pending
    description = Column(String(256), default="")
    last_sync_at = Column(DateTime, nullable=True)
    total_rows = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())


class SyncTask(Base):
    __tablename__ = "sync_task"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=False)
    title = Column(String(128), nullable=False)
    added_rows = Column(Integer, nullable=False, default=0)
    skipped_rows = Column(Integer, nullable=False, default=0)   # 去重跳过的重复行
    status = Column(String(16), nullable=False, default="success")  # success / partial / failed
    detail = Column(String(256), default="")
    started_at = Column(DateTime, server_default=func.now())


# ---------- 维度层 ----------
class DimGame(Base):
    __tablename__ = "dim_game"
    id = Column(Integer, primary_key=True)
    code = Column(String(16), unique=True, nullable=False)      # gi / hsr
    name = Column(String(64), nullable=False)
    publisher = Column(String(64), default="miHoYo")


class DimVersion(Base):
    __tablename__ = "dim_version"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    code = Column(String(16), nullable=False)                    # 5.2
    title = Column(String(128), default="")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    UniqueConstraint("game_id", "code", name="uq_version")


class DimBanner(Base):
    __tablename__ = "dim_banner"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("dim_version.id"), nullable=True)
    name = Column(String(128), nullable=False)
    banner_type = Column(String(32), default="character")        # character / weapon / standard
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)


class DimItem(Base):
    __tablename__ = "dim_item"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    external_item_id = Column(String(32), nullable=False)        # UIGF 的 item_id
    name = Column(String(128), nullable=False)
    item_type = Column(String(32), default="character")          # character / weapon
    rarity = Column(Integer, nullable=False, default=3)          # 3/4/5 星
    UniqueConstraint("game_id", "external_item_id", name="uq_item")


class DimPlayer(Base):
    __tablename__ = "dim_player"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    external_uid = Column(String(32), nullable=False)
    nickname = Column(String(64), default="")
    channel = Column(String(32), default="official")             # official / bilibili / taptap / ios
    register_date = Column(Date, nullable=False)
    level = Column(Integer, default=1)
    payer_tier = Column(String(16), default="free")              # free / minnow 月卡党 / dolphin 中R / whale 大R
    total_spend = Column(Float, default=0)
    last_active_date = Column(Date, nullable=True)
    UniqueConstraint("game_id", "external_uid", name="uq_player")


# ---------- 事实层 ----------
class FactEventLog(Base):
    """通用事件流水：登录、新手步骤、关卡、活动参与等都记在这里（生产环境按月分区）"""
    __tablename__ = "fact_event_log"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("dim_player.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)
    event_name = Column(String(48), nullable=False)              # login / tutorial_step / level_clear ...
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(DateTime, nullable=True)
    props = Column(Text, default="")                             # JSON 字符串：step=4 等附加属性
    Index("ix_event_game_date_name", "game_id", "event_date", "event_name")


class FactSession(Base):
    __tablename__ = "fact_session"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("dim_player.id"), nullable=False)
    session_date = Column(Date, nullable=False, index=True)
    duration_min = Column(Float, default=0)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)


class FactPayment(Base):
    __tablename__ = "fact_payment"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("dim_player.id"), nullable=False)
    banner_id = Column(Integer, ForeignKey("dim_banner.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)
    external_id = Column(String(64), nullable=True)
    amount = Column(Float, nullable=False)                       # 元
    product = Column(String(64), default="")                     # 月卡 / 648 礼包 ...
    paid_at = Column(DateTime, nullable=False)
    pay_date = Column(Date, nullable=False, index=True)
    UniqueConstraint("game_id", "external_id", name="uq_payment_ext")


class FactGacha(Base):
    __tablename__ = "fact_gacha"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("dim_player.id"), nullable=False)
    banner_id = Column(Integer, ForeignKey("dim_banner.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("dim_item.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)
    external_id = Column(String(64), nullable=True)              # UIGF/SRGF 的记录 id，去重靠它
    banner_type = Column(String(32), default="character")
    rarity = Column(Integer, nullable=False, default=3)
    pity_count = Column(Integer, default=0)                      # 这一抽距离上个五星第几抽
    pulled_at = Column(DateTime, nullable=False)
    pull_date = Column(Date, nullable=False, index=True)
    UniqueConstraint("game_id", "external_id", name="uq_gacha_ext")


class FactFeedback(Base):
    __tablename__ = "fact_feedback"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("dim_version.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("data_source.id"), nullable=True)
    external_id = Column(String(64), nullable=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)                      # 1-5 星（平台评分，可空）
    sentiment = Column(Float, nullable=True)                     # -1..1（阶段 8 由模型回填，生成器先给模拟值）
    aspect = Column(String(32), default="")                      # 剧情/角色/美术音乐/玩法/优化卡顿/抽卡福利
    created_at = Column(DateTime, nullable=False)
    fb_date = Column(Date, nullable=False, index=True)
    UniqueConstraint("game_id", "external_id", name="uq_feedback_ext")


class FactDailyMetric(Base):
    """日粒度预聚合：总览页直接读它，不扫流水表"""
    __tablename__ = "fact_daily_metric"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    metric_date = Column(Date, nullable=False, index=True)
    dau = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    pay_users = Column(Integer, default=0)
    sessions = Column(Integer, default=0)
    UniqueConstraint("game_id", "metric_date", name="uq_metric_day")


class FactRetentionCohort(Base):
    """按周注册队列的留存（注册日所在周为一期）"""
    __tablename__ = "fact_retention_cohort"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    cohort_week = Column(Date, nullable=False)                   # 该周周一
    cohort_size = Column(Integer, default=0)
    d1 = Column(Float, default=0)                                # 次日留存率 0..1
    d7 = Column(Float, default=0)
    d30 = Column(Float, default=0)
    UniqueConstraint("game_id", "cohort_week", name="uq_cohort")


# ---------- 分析枢纽 ----------
class PlayerFeatureSnapshot(Base):
    """玩家特征快照：分群/流失/LTV 共用；按 run_date 版本化，不覆盖历史"""
    __tablename__ = "player_feature_snapshot"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("dim_game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("dim_player.id"), nullable=False)
    run_date = Column(Date, nullable=False)
    recency_days = Column(Integer, default=0)
    frequency_30d = Column(Integer, default=0)
    monetary_30d = Column(Float, default=0)
    orders_30d = Column(Integer, default=0)  # 近 30 天付费次数（F 的全量补强项）
    avg_session_min = Column(Float, default=0)
    level = Column(Integer, default=1)
    gacha_pulls_30d = Column(Integer, default=0)
    UniqueConstraint("game_id", "player_id", "run_date", name="uq_snapshot")
