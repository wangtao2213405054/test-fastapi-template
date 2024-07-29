# 基于 FastAPI 的自动化测试平台项目

## 本地调试

### 首次构建
1. 复制环境变量信息 `cp .env.example .env`
2. 创建 Docker 网络 `docker network create app_main`
3. 构建 Docker 镜像 `docker compose up -d --build`


### 数据迁移
1. 首次构建后使用 `docker compose exec app migrate` 来初始化数据库