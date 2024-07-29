# _author: Coke
# _date: 2024/7/28 14:05
# _description: Docker 镜像部署服务器

# 使用 Python 3.12.4 为镜像
FROM python:3.12.4-slim-bookworm

# 更新包管理器的索引并安装系统依赖
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/*

# 设置 Python 环境变量
# 防止生成 .pyc 文件
# 确保输出不适用缓冲
# IO编码为 UTF-8
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# 复制文件到临时目录
COPY requirements/ /tmp/requirements

# 安装项目依赖
RUN pip install -U pip && \
    pip install --no-cache-dir -r /tmp/requirements/dev.txt

# 将 当前目录复制到镜像的 src 目录
COPY . /src
ENV PATH "$PATH:/src/scripts"

# 创建新用户并设置目录权限
RUN useradd -m -d /src -s /bin/bash app \
    && chown -R app:app /src/* && chmod +x /src/scripts/*

# 设置工作目录并切换至 app 用户
WORKDIR /src
USER app

# 指定容器启动服务
CMD ["./scripts/run-dev.sh"]
