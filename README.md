# 基于 FastAPI 的自动化测试平台项目

## 本地调试

### 首次构建
1. 复制环境变量信息 `cp .env.example .env`
2. 创建 Docker 网络 `docker network create app_main`
3. 构建 Docker 镜像 `docker compose up -d --build`


### 数据迁移
1. 首次构建后使用 `docker compose exec app migrate` 来初始化数据库


## Git 提交规范

### 格式
```text
    <type>(scope): <description>
    
    [optional body]

    [optional footer(s)]
```
### 提交类别
- feat: 新特性
- fix: 修复 bug
- docs: 仅文档修改
- style: 格式化代码
- refactor: 代码重构及优化
- test: 添加缺失的测试或修复现有测试
- chore: 维护任务（如构建过程或辅助工具的更改）

### scope: 可选，指明提交影响的范围（例如某个模块或功能）。
### description: 提交的简短描述。
### body: 可选的详细说明，解释提交的背景、动机和影响。
### footer: 可选的脚注，通常用于引用相关问题或 PR（pull request）编号。

### 示例
```text
    refactor(database): 优化数据库连接相关
    
    重构了查询、更新、方法
    对获取 Session 方法进行了优化
```