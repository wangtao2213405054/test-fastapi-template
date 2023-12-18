
from fastapi import APIRouter
from typing import Any

from src.auth.schemas import (
    AuthLoginRequest,
    AccessTokenResponse,
    AuthGetMenuRequest,
    AuthEditMenuRequest
)
from src.auth.service import get_menu_tree, edit_menu
from src.schemas import ResponseModel
from src.auth import jwt

from src.database import fetch_one, insert_one

from src.auth.models import (
    UserTable,
    UserCreate,
    MenuInfoResponse,
    MenuListResponse
)
from src.websocketio import socket
from sqlmodel import select


router = APIRouter(prefix="/auth")


@router.post("/user/login")
async def user_login(body: AuthLoginRequest) -> ResponseModel[AccessTokenResponse]:
    """
    用户登录接口\f
    :param body: <AuthLoginRequest> 对象
    :return:
    """
    user = UserCreate(
        name="郭聪",
        email="2213405052@qq.com",
        mobile="13520421041",
        password="1123",
        nodeId=1,
        roleId=1
    )

    await insert_one(UserTable, user)
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


@router.post("/menu/list")
async def menu_list(body: AuthGetMenuRequest) -> ResponseModel[list[MenuListResponse]]:
    """
    获取权限菜单列表\f
    :param body: <AuthGetMenuRequest> 对象
    :return:
    """
    menus = await get_menu_tree(body.nodeId, body.keyword)
    return ResponseModel(data=menus)


@router.post("/menu/edit")
async def menu_edit(body: AuthEditMenuRequest) -> ResponseModel[MenuInfoResponse]:
    """
    添加/更新 一个权限菜单\f
    :param body: AuthAddMenuRequest<对象>
    :return:
    """
    menu = await edit_menu(
        menu_id=body.id, name=body.name, identifier=body.identifier, node_id=body.nodeId
    )
    return ResponseModel(data=menu)


@socket.event
def connect(sid: str, environ: dict[str, Any]):
    """
    socketio 连接事件
    :return:
    """
    token = environ.get("HTTP_TOKEN")
    print(token, 'token')
    print(socket.rooms(sid), 'rooms')
    # if not token:
    #     return False


@socket.event
def disconnect(sid: str):
    """
    socketio 断连事件
    :return:
    """
    print(sid, '123')
