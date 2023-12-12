
from fastapi import APIRouter

from src.auth.schemas import AuthLoginRequest, AccessTokenResponse
from src.schemas import ResponseModel
from src.auth import jwt

from src.exceptions import NotAuthenticated

router = APIRouter(prefix="/auth")


@router.post("/user/login")
async def user_login(body: AuthLoginRequest) -> ResponseModel[AccessTokenResponse]:
    """ 获取用户令牌 """
    return ResponseModel(
        data=AccessTokenResponse(
            accessToken=jwt.create_access_token(user={'id': 1, 'is_admin': True}),
            refreshToken="333"
        )
    )


@router.post("/user/test")
async def user_test():
    raise NotAuthenticated()
