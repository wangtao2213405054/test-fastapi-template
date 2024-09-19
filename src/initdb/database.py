# _author: Coke
# _date: 2024/9/14 上午10:04
# _description:

from sqlmodel import Session, create_engine

from src.config import settings


async def session() -> Session:
    """
    Fixture 用于创建和管理异步数据库会话。

    该 fixture 设置了一个异步 SQLite 数据库连接，创建所需的表，
    并提供一个会话实例以供测试使用。

    :return: 异步数据库会话实例
    """

    # 将数据库连接配置到 alembic.ini 中
    database_url = str(settings.DATABASE_URL)

    db_driver = settings.DATABASE_URL.scheme

    # 如果存在异步驱动则更改为同步
    db_driver_parts = db_driver.split("+")
    if len(db_driver_parts) > 1:
        sync_scheme = f"{db_driver_parts[0].strip()}+mysqlconnector"
        database_url = database_url.replace(db_driver, sync_scheme)

    engine = create_engine(database_url, echo=True)

    async with Session(engine) as _session:
        yield _session
