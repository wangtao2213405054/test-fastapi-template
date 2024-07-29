# _author: Coke
# _date: 2024/7/28 00:45
# _description: 认证相关错误信息


class ErrorCode:
    """认证错误码实例"""

    AUTHENTICATION_REQUIRED = "需要身份验证"
    AUTHORIZATION_FAILED = "授权失败，用户没有访问权限"
    INVALID_TOKEN = "无效令牌"
    INVALID_CREDENTIALS = "无效的凭证"
    REFRESH_TOKEN_NOT_VALID = "刷新令牌无效"
    INVALID_PASSWORD = "无效密码"
    PASSWORD_WRONG = "密码错误"
    PASSWORD_STANDARDS = "密码不符合规则"
    INVALID_USERNAME = "用户名不存在"
