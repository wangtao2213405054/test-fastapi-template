# _author: Coke
# _date: 2024/7/25 14:15
# _description: 用户验证相关路由

from fastapi import APIRouter
from typing import Any

from .models.types import (
    AuthLoginRequest, AccessTokenResponse,
    CreateUserRequest,
    AuthGetMenuRequest, AuthEditMenuRequest,
    AuthEditRoleRequest, AuthGetRoleListRequest,
    AuthEditAffiliationRequest, AuthGetAffiliationListRequest
)
from .service import (
    get_public_key, create_user,
    edit_role, get_role_list, delete_role,
    edit_menu, get_menu_tree, delete_menu,
    edit_affiliation, get_affiliation_tree, delete_affiliation
)
from src.models.types import ResponseModel, DeleteRequestModel
from src.api.auth import jwt

from src.database import fetch_one, insert_one

from .models.models import (
    UserTable, UserCreate,
    MenuInfoResponse, MenuListResponse,
    RoleInfoResponse,
    AffiliationListResponse, AffiliationInfoResponse
)
from src.websocketio import socket
from sqlmodel import select


router = APIRouter(prefix="/auth")


@router.get("/public/key")
def user_public_key() -> ResponseModel[str]:
    """
    获取密码公钥\f
    :return:
    """
    public_key = get_public_key()
    return ResponseModel(data=public_key)


@router.post("/user/create")
async def user_edit(body: CreateUserRequest):
    await create_user(
        name=body.name,
        email=body.email,
        mobile=body.mobile,
        password=body.password,
        affiliation_id=body.affiliationId
    )
    return None


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
    menus = await get_menu_tree(node_id=body.nodeId, keyword=body.keyword)
    return ResponseModel(data=menus)


@router.put("/menu/edit")
async def menu_edit(body: AuthEditMenuRequest) -> ResponseModel[MenuInfoResponse]:
    """
    添加/更新 一个权限菜单\f
    :param body: <AuthAddMenuRequest> 对象
    :return:
    """
    menu = await edit_menu(
        menu_id=body.id, name=body.name, identifier=body.identifier, node_id=body.nodeId
    )
    return ResponseModel(data=menu)


@router.delete("/menu/delete")
async def menu_delete(body: DeleteRequestModel) -> ResponseModel[MenuInfoResponse]:
    """
    删除一个权限菜单\f
    :param body: <DeleteRequestModel> 对象
    :return:
    """
    menu = await delete_menu(menu_id=body.id)
    return ResponseModel(data=menu)


@router.put("/role/edit")
async def role_edit(body: AuthEditRoleRequest) -> ResponseModel:
    """
    添加/修改 一个角色信息\f
    :param body: <AuthEditRoleRequest> 对象
    :return:
    """
    await edit_role(
        role_id=body.id,
        name=body.name,
        identifier=body.identifier,
        identifier_list=body.menuIdentifierList
    )

    return ResponseModel()


@router.post("/role/list")
async def role_list(body: AuthGetRoleListRequest) -> ResponseModel[list[RoleInfoResponse]]:
    """
    获取角色列表\f
    :param body: <AuthGetRoleListRequest> 对象
    :return:
    """
    role = await get_role_list(
        body.page,
        body.pageSize,
        keyword=body.keyword
    )

    return ResponseModel(data=role)


@router.delete("/role/delete")
async def role_delete(body: DeleteRequestModel) -> ResponseModel[RoleInfoResponse]:
    """
    删除一个角色信息\f
    :param body: <DeleteRequestModel> 对象
    :return:
    """
    role = await delete_role(role_id=body.id)
    return ResponseModel(data=role)


@router.put("/affiliation/edit")
async def affiliation_edit(body: AuthEditAffiliationRequest) -> ResponseModel[AffiliationInfoResponse]:
    """
    新增/修改 一个所属关系信息\f
    :param body: <AuthEditAffiliationRequest> 对象
    :return:
    """
    affiliation = await edit_affiliation(affiliation_id=body.id, name=body.name, node_id=body.nodeId)
    return ResponseModel(data=affiliation)


@router.post("/affiliation/list")
async def affiliation_list(body: AuthGetAffiliationListRequest) -> ResponseModel[list[AffiliationListResponse]]:
    """
    获取所属关系列表\f
    :param body: <AuthGetAffiliationListRequest> 对象
    :return:
    """

    affiliation = await get_affiliation_tree(node_id=body.nodeId, keyword=body.keyword)
    return ResponseModel(data=affiliation)


@router.delete("/affiliation/delete")
async def affiliation_delete(body: DeleteRequestModel) -> ResponseModel[AffiliationInfoResponse]:
    """
    删除所有关系信息\f
    :param body: <DeleteRequestModel> 对象
    :return:
    """
    affiliation = await delete_affiliation(affiliation_id=body.id)
    return ResponseModel(data=affiliation)


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
