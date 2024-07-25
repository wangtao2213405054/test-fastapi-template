from src.api.auth.constants import ErrorCode
from src.exceptions import NotAuthenticated, PermissionDenied


class AuthRequired(NotAuthenticated):
    """ 需要身份验证 """
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    """ 无访问权限 """
    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidToken(NotAuthenticated):
    """ 无效令牌 """
    DETAIL = ErrorCode.INVALID_TOKEN


class InvalidCredentials(NotAuthenticated):
    """ 无效凭证 """
    DETAIL = ErrorCode.INVALID_CREDENTIALS


class RefreshTokenNotValid(NotAuthenticated):
    """ 刷新令牌无效 """
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID
