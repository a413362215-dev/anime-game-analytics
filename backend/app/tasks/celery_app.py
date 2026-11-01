from celery import Celery
from ..core.config import settings

celery_app = Celery("aga", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
# 阶段3起注册定时任务：ETL 聚合 / 模型训练 / 情感分析 / 向量索引
