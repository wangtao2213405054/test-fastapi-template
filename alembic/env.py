# _author: Coke
# _date: 2024/7/29 16:37
# _description: Alembic 迁移文件, 包含 Alembic 环境、数据库连接、上下文配置及迁移脚本

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.config import settings

from sqlmodel import SQLModel

# 需要导入要创建的模型信息, 由 Alembic 自动创建对应的数据表
from src.api.manage.models import (
    UserTable,
    RoleTable,
    AffiliationTable,
    MenuTable
)

# 这是 Alembic 配置对象，它提供了对所使用的 .ini 文件中值的访问
config = context.config

# 用于 Python 日志记录的配置文件
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 将模型设置为 SQLModel 的 Metadata
target_metadata = SQLModel.metadata

# 将数据库连接配置到 alembic.ini 中
DATABASE_URL = str(settings.DATABASE_URL)

db_driver = settings.DATABASE_URL.scheme

# 如果存在异步驱动则更改为同步
db_driver_parts = db_driver.split("+")
if len(db_driver_parts) > 1:
    # 非 Mysql 数据库请修改此部分内容, 采用了 mysql connector 连接方式
    sync_scheme = f'{db_driver_parts[0].strip()}+mysqlconnector'
    DATABASE_URL = DATABASE_URL.replace(db_driver, sync_scheme)

config.set_main_option("sqlalchemy.url", DATABASE_URL)
config.compare_type = True
config.compare_server_default = True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
