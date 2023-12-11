
from fastapi import APIRouter

from src.auth.schemas import AuthLoginRequest, AuthLoginResponse

router = APIRouter(prefix="/auth")


@router.post("/user/login")
async def user_login(body: AuthLoginRequest) -> AuthLoginResponse:
    """
    获取用户令牌
    :param body: <AuthLoginRequest> 对象
    :return:
    """
    return AuthLoginResponse(token="123", refreshToken="333")
