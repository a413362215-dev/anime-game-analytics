from fastapi import APIRouter

router = APIRouter(tags=["system"])

PAGES = [
    {"path": "/dashboard",  "title": "总览看板",   "stage": 3},
    {"path": "/segment",    "title": "玩家分群",   "stage": 5},
    {"path": "/funnel",     "title": "行为漏斗",   "stage": 3},
    {"path": "/churn",      "title": "流失预警",   "stage": 6},
    {"path": "/ltv",        "title": "LTV预测",    "stage": 7},
    {"path": "/experiment", "title": "A/B实验",    "stage": 9},
    {"path": "/gacha",      "title": "付费与抽卡", "stage": 4},
    {"path": "/feedback",   "title": "版本反馈",   "stage": 8},
    {"path": "/chat",       "title": "LLM智能助手", "stage": 10},
    {"path": "/data",       "title": "数据管理",   "stage": 2},
]

@router.get("/health")
def health():
    return {"status": "ok", "service": "anime-game-analytics"}

@router.get("/system/pages")
def pages():
    """前端菜单的单一事实来源：页面与路线图阶段对应"""
    return PAGES
