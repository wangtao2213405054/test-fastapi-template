# _author: Coke
# _date: 2024/7/28 00:54
# _description: 数据库异常

from typing import Any

from src.exceptions import message, status

from .http import DetailedHTTPException


class DatabaseConflictError(DetailedHTTPException):
    """数据库基础错误"""

    STATUS_CODE = status.DATABASE_600_BAD_SQL
    DETAIL = message.DATABASE_600_BAD_SQL

    def __init__(self, detail: dict | None, **kwargs: dict[str, Any]) -> None:
        super(DatabaseConflictError, self).__init__(**kwargs)
        self.ERRORS = detail


class DatabaseNotFound(DetailedHTTPException):
    """无法在数据库找到对应信息"""

    STATUS_CODE = status.DATABASE_610_NOT_FOUND
    DETAIL = message.DATABASE_610_NOT_FOUND


class DatabaseUniqueError(DetailedHTTPException):
    """数据在数据库中已存在"""

    STATUS_CODE = status.DATABASE_611_UNIQUE
    DETAIL = message.DATABASE_611_UNIQUE

    def __init__(self, detail: str, **kwargs: dict[str, Any]) -> None:
        super(DatabaseUniqueError, self).__init__(**kwargs)
        self.DETAIL = detail
