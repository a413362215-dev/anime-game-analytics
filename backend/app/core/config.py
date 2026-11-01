import os

class Settings:
    """配置全部走环境变量；本地开发给默认值，正式部署用 .env 覆盖。"""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.deepseek.com")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")

settings = Settings()
