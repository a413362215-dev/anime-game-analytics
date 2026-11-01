# 二次元游戏玩家行为分析系统 Anime Game Analytics

基于 Python + Vue 的二次元游戏玩家行为分析系统：玩家行为分析 + 版本反馈分析 + LLM 智能聊天。
借鉴参考项目 JayDS22/Game-Monetization-LiveOps-Analytics 的模块划分，按自定路线图分 12 阶段推进（阶段 0 设计定版已完成，本仓库为阶段 1 骨架）。

## 技术栈
- 前端：Vue 3 + Vite + TypeScript + Pinia + Vue Router + Element Plus + ECharts
- 后端：FastAPI + SQLAlchemy + Pydantic + JWT，异步任务 Celery + Redis
- 数据库：PostgreSQL 16（pgvector 镜像）—— 本地快速体验时后端默认用 SQLite
- 部署：Docker Compose（db / redis / backend / frontend 四个服务）

## 仓库用 GitHub，运行用 Docker（两者不冲突）
- Git/GitHub 管代码版本：改坏了能回退、多人能协作、论文答辩能展示提交记录。
- Docker 管运行环境：一条 `docker compose up` 在任何机器上还原同一套 PG/Redis/前后端。
- 本地先 `git init`，在 GitHub 建空仓库后 `git remote add origin <地址>` 再 push 即可。

## 快速开始
### 方式 A：Docker（推荐，最终形态）
```bash
cp .env.example .env
docker compose up -d --build
# 前端 http://localhost:5173  后端 http://localhost:8000/docs
```
### 方式 B：本地开发（不用 Docker 先跑通逻辑）
```bash
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000   # 默认 SQLite，自动建表+种子账号
cd ../frontend && npm install && npm run dev          # http://localhost:5173
```
## 种子账号（首次启动自动创建，正式环境请改密）
- 管理员 admin / admin123
- 分析师 analyst / analyst123

## 目录
见 docs/项目目录说明.md；开发顺序见路线图（阶段 0~11）。
