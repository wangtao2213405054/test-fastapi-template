# _author: Coke
# _date: 2024/7/25 14:15
# _description: 用户验证公开路由

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import jwt
from src.models.types import ResponseModel

from .models.types import AccessTokenResponse, AuthLoginRequest, RefreshTokenRequest, SwaggerToken
from .service import authenticate_user, decrypt_password, get_public_key

router = APIRouter(prefix="/auth")


@router.get("/public/key")
def user_public_key() -> ResponseModel[str]:
    """
    获取密码公钥\f

    :return:
    """
    public_key = get_public_key()
    return ResponseModel(data=public_key)


@router.post("/swagger/login", deprecated=True, dependencies=[])
async def swagger_login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> SwaggerToken:
    """
    Swagger 登录接口, 用于 Swagger 文档的登录 只有在开发环境中可以调用\n
    注意!!! 此接口传递的密码没有进行加密, 请谨慎...\f

    :param form: <OAuth2PasswordRequestForm> 对象
    :return:
    """
    user = await authenticate_user(form.username, form.password)

    return SwaggerToken(access_token=jwt.create_access_token(user=dict(id=user.id)), token_type="bearer")


@router.post("/user/login")
async def user_login(body: AuthLoginRequest) -> ResponseModel[AccessTokenResponse]:
    """
    登录接口 \f

    :param body: <AuthLoginRequest> 对象
    :return:
    """
    user = await authenticate_user(body.username, decrypt_password(body.password))
    token = jwt.create_access_token(user=dict(id=user.id))

    refresh_token = jwt.create_refresh_token(user=dict(id=user.id))

    return ResponseModel(data=AccessTokenResponse(accessToken=token, refreshToken=refresh_token))


@router.post("/refresh/token")
async def refresh_user_token(body: RefreshTokenRequest) -> ResponseModel[AccessTokenResponse]: ...
