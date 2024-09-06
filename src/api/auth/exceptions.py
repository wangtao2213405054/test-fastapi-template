# _author: Coke
# _date: 2024/7/27 15:41
# _description: 用户认证相关异常


from src.api.auth.constants import ErrorCode
from src.exceptions import BadData, NotAuthenticated, PermissionDenied
from src.exceptions.status import HTTP_471_INVALID_REFRESH_TOKEN


class AuthRequired(NotAuthenticated):
    """需要身份验证"""

    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    """无访问权限"""

    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidToken(NotAuthenticated):
    """无效令牌"""

    DETAIL = ErrorCode.INVALID_TOKEN


class InvalidCredentials(NotAuthenticated):
    """无效凭证"""

    DETAIL = ErrorCode.INVALID_CREDENTIALS


class RefreshTokenNotValid(NotAuthenticated):
    """刷新令牌无效"""

    STATUS_CODE = HTTP_471_INVALID_REFRESH_TOKEN
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID


class InvalidUsername(BadData):
    """不存在的用户名"""

    DETAIL = ErrorCode.INVALID_USERNAME


class InvalidPassword(BadData):
    """无效密码"""

    DETAIL = ErrorCode.INVALID_PASSWORD


class WrongPassword(BadData):
    """密码错误"""

    DETAIL = ErrorCode.PASSWORD_WRONG


class StandardsPassword(BadData):
    """密码不符合规范"""

    DETAIL = ErrorCode.PASSWORD_STANDARDS
