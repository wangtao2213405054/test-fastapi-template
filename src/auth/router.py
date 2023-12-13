
from fastapi import APIRouter

from src.auth.schemas import AuthLoginRequest, AccessTokenResponse
from src.schemas import ResponseModel
from src.auth import jwt

from src.database import fetch_one

from src.auth.models import UserTable
from sqlmodel import select

from src.auth.exceptions import AuthRequired


router = APIRouter(prefix="/auth")


@router.post("/user/login")
async def user_login(body: AuthLoginRequest) -> ResponseModel[AccessTokenResponse]:
    """
    用户登录接口\f
    :param body: <AuthLoginRequest> 对象
    :return:
    """
    return ResponseModel(
        data=AccessTokenResponse(
            accessToken=jwt.create_access_token(user={'id': 1, 'is_admin': True}),
            refreshToken="333"
        )
    )


@router.post("/user/test")
async def user_test():
    user = await fetch_one(select(UserTable).where(UserTable.id == 2))
    return user
