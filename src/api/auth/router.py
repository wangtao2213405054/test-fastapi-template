# _author: Coke
# _date: 2024/8/26 下午3:51
# _description: 用户认证相关路由

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import jwt
from src.api.manage.models import UserResponse
from src.config import debug
from src.models.types import ResponseModel
from src.websocketio import socket

from .models import AccessTokenResponse, SwaggerToken
from .service import authenticate_user, get_current_user, get_public_key, login, refresh_token
from .types import AuthLoginRequest, JWTData, RefreshTokenRequest

router = APIRouter(prefix="/auth")


@router.get("/getPublicKey")
def user_public_key() -> ResponseModel[str]:
    """
    获取密码公钥接口

    获取用于加密用户密码的公钥。\f

    :return: 包含公钥的 <ResponseModel> 对象
    """
    public_key = get_public_key()
    return ResponseModel(data=public_key)


@router.post("/swaggerLogin", deprecated=True, dependencies=[Depends(debug)])
async def swagger_login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> SwaggerToken:
    """
    Swagger 登录接口 (仅在开发环境中使用)

    用于 Swagger 文档的登录功能，注意此接口的密码没有进行加密，因此仅在开发环境中使用。\n
    注意!!! 此接口传递的密码没有进行加密, 请谨慎使用...\f

    :param form: 包含用户名和密码的 <OAuth2PasswordRequestForm> 对象
    :return: 包含访问令牌的 <SwaggerToken> 对象
    """
    user = await authenticate_user(form.username, form.password)
    return SwaggerToken(
        access_token=jwt.create_access_token(user=JWTData(userId=user.id)),
        token_type="bearer",
    )


@router.post("/userLogin")
async def user_login(body: AuthLoginRequest) -> ResponseModel[AccessTokenResponse]:
    """
    用户登录接口

    用户通过提供用户名和密码来登录系统。密码在发送前会被解密。成功后，返回访问令牌和刷新令牌。\f

    :param body: 包含用户名和加密密码的 <AuthLoginRequest> 对象
    :return: 包含访问令牌和刷新令牌的 <ResponseModel> 对象
    """

    response: AccessTokenResponse = await login(body.username, body.password)

    return ResponseModel(data=response)


@router.post("/refreshToken")
async def refresh_user_token(body: RefreshTokenRequest) -> ResponseModel[AccessTokenResponse]:
    """
    刷新用户令牌接口

    使用刷新令牌来生成新的 Token。此接口允许用户在原有的 Token 过期后获取新的 Token \f

    :param body: 包含刷新令牌的 <RefreshTokenRequest> 对象
    :return: 包含新生成的访问令牌和刷新令牌的 <ResponseModel> 对象
    """

    response: AccessTokenResponse = await refresh_token(body.refreshToken)
    return ResponseModel(data=response)


@router.get("/getUserInfo", dependencies=[Depends(jwt.parse_jwt_user_data)])
async def user_info(
    user: Annotated[UserResponse, Depends(get_current_user)],
) -> ResponseModel[UserResponse]:
    """
    获取当前用户信息接口

    获取当前登录用户的信息。通过 JWT 获取用户数据，并返回用户信息。\f

    :param user: 当前用户信息，由 JWT 解析函数提供
    :return: 包含用户信息的 <ResponseModel> 对象
    """
    return ResponseModel(data=user)


@socket.event
def connect(sid: str, environ: dict[str, Any]) -> None:
    """
    socketio 连接事件

    当一个新的 socketio 客户端连接时触发。可以在这里进行身份验证或者连接管理。

    :param sid: socketio 连接的会话 ID
    :param environ: 环境信息，包括请求头和其他连接信息
    """
    token = environ.get("HTTP_TOKEN")
    print(token, "token")
    print(socket.rooms(sid), "rooms")
    # if not token:
    #     return False


@socket.event
def disconnect(sid: str) -> None:
    """
    socketio 断连事件

    当一个 socketio 客户端断开连接时触发。可以在这里处理断连后的清理工作。

    :param sid: socketio 断开连接的会话 ID
    """
    print(sid, "123")
