# _author: Coke
# _date: 2024/7/29 15:05
# _description: 使用 Just 来简化命令, 需安装 Just 使用

# 获取 just 命令列表
default:
  just --list

# 复制环境文件
env:
  cp .env.example .env

# 创建 Docker 网络
network:
  docker network create app_main

# 启动 Docker Compose 中的服务
up:
  docker compose up -d

# 停止 Docker Compose 中的服务
stop:
  docker compose stop

# 杀死 Docker Compose 中的服务
kill:
  docker compose kill

# 构建 Docker Compose 镜像
build:
  docker compose build

# 获取当前 Docker Compose 容器列表
ps:
  docker compose ps

# 删除当前所有容器
rm *args:
  @if [ "{{args}}" = "-f" ]; then \
    docker rm -f $(docker ps -aq); \
  else \
    docker rm $(docker ps -aq); \
  fi

# 删除当前所有的镜像
rmi:
  docker rmi $(docker images -q)

# 将 Docker 中的数据库迁移至最新版本
migrate:
  docker compose exec app migrate

# 将 Docker 中的数据库回滚到指定版本
downgrade *args:
  docker compose exec app downgrade {{args}}

# 生成数据库同步脚本
makemigrations *args:
  docker compose exec app makemigrations {{args}}

# 将 Docker 中的代码使用 ruff 格式化
ruff *args:
  docker compose exec app format {{args}}

# 使用 mypy 进行代码静态检查
mypy:
  docker compose exec app mypy /src/src

# 运行单元测试
pytest:
  docker compose exec app pytest
