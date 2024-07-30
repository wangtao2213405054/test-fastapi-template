# _author: Coke
# _date: 2024/7/28 00:53
# _description: 请求异常基础类

from typing import Any

from fastapi import HTTPException
from fastapi import status as http_status

from src.exceptions import message, status


class DetailedHTTPException(HTTPException):
    STATUS_CODE = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = message.HTTP_500_INTERNAL_SERVER_ERROR
    ERRORS: dict | None = None

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    """权限校验失败"""

    STATUS_CODE = http_status.HTTP_403_FORBIDDEN
    DETAIL = message.HTTP_403_FORBIDDEN


class NotFound(DetailedHTTPException):
    """资源未找到"""

    STATUS_CODE = http_status.HTTP_404_NOT_FOUND
    DETAIL = message.HTTP_404_NOT_FOUND


class BadRequest(DetailedHTTPException):
    """请求错误"""

    STATUS_CODE = http_status.HTTP_400_BAD_REQUEST
    DETAIL = message.HTTP_400_BAD_REQUEST


class BadData(DetailedHTTPException):
    """错误数据"""

    STATUS_CODE = status.HTTP_461_BAD_DATA
    DETAIL = message.HTTP_461_BAD_DATA


class NotAuthenticated(DetailedHTTPException):
    """用户认证失败"""

    STATUS_CODE = http_status.HTTP_401_UNAUTHORIZED
    DETAIL = message.HTTP_401_UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
