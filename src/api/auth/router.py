# _author: Coke
# _date: 2024/7/25 14:15
# _description: 用户验证相关路由

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.models.types import DeleteRequestModel, ResponseModel
from src.websocketio import socket

from .jwt import validate_permission
from .models import (
    AffiliationInfoResponse,
    AffiliationListResponse,
    MenuInfoResponse,
    MenuListResponse,
    RoleInfoResponse,
    UserResponse,
)
from .types import (
    AuthEditAffiliationRequest,
    AuthEditMenuRequest,
    AuthEditRoleRequest,
    AuthGetAffiliationListRequest,
    AuthGetMenuRequest,
    AuthGetRoleListRequest,
    CreateUserRequest,
    UpdatePasswordRequest,
    UpdateUserInfoRequest,
)
from .service import (
    create_user,
    delete_affiliation,
    delete_menu,
    delete_role,
    edit_affiliation,
    edit_menu,
    edit_role,
    get_affiliation_tree,
    get_current_user,
    get_menu_tree,
    get_role_list,
    update_password,
    update_user,
)

router = APIRouter(prefix="/auth", dependencies=[Depends(validate_permission)])


@router.post("/user/create")
async def user_edit(body: CreateUserRequest) -> ResponseModel[UserResponse]:
    """
    创建用户接口

    创建一个新的用户。需要提供用户的名称、邮箱、手机号码、密码、所属关系 ID 和（可选的）头像 URL 和角色 ID。\f

    :param body: 包含用户信息的 <CreateUserRequest> 对象
    :return: 包含新创建用户信息的 <ResponseModel> 对象
    """
    user = await create_user(
        name=body.name,
        email=body.email,
        mobile=body.mobile,
        password=body.password,
        affiliation_id=body.affiliationId,
    )
    return ResponseModel(data=user)


@router.post("/user/update")
async def user_update(body: UpdateUserInfoRequest) -> ResponseModel[UserResponse]:
    """
    修改用户信息接口

    更新现有用户的信息。可以修改用户的名称、邮箱、手机号码、状态、所属关系 ID、头像 URL 和角色 ID。\f

    :param body: 包含用户信息的 <UpdateUserInfoRequest> 对象
    :return: 包含更新后用户信息的 <ResponseModel> 对象
    """
    user = await update_user(
        user_id=body.id,
        name=body.name,
        email=body.email,
        mobile=body.mobile,
        status=body.status,
        affiliation_id=body.affiliationId,
        avatar=body.avatarUrl,
        role_id=body.roleId,
    )
    return ResponseModel(data=user)


@router.post("/update/password")
async def user_update_password(body: UpdatePasswordRequest) -> ResponseModel:
    """
    修改用户密码接口

    更新用户的密码。需要提供用户 ID、旧密码和新密码。\f

    :param body: 包含密码信息的 <UpdatePasswordRequest> 对象
    :return: 无内容的 <ResponseModel> 对象
    """
    await update_password(user_id=body.id, old_password=body.oldPassword, new_password=body.newPassword)
    return ResponseModel()


@router.get("/user/info")
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


@router.post("/menu/list")
async def menu_list(body: AuthGetMenuRequest) -> ResponseModel[list[MenuListResponse]]:
    """
    获取权限菜单列表接口

    获取指定节点的权限菜单列表，并可以通过关键字进行过滤。\f

    :param body: 包含节点 ID 和关键字的 <AuthGetMenuRequest> 对象
    :return: 包含菜单列表的 <ResponseModel> 对象
    """
    menus = await get_menu_tree(node_id=body.nodeId, keyword=body.keyword)
    return ResponseModel(data=menus)


@router.put("/menu/edit")
async def menu_edit(body: AuthEditMenuRequest) -> ResponseModel[MenuInfoResponse]:
    """
    添加或更新权限菜单接口

    根据提供的菜单 ID 更新菜单信息，如果 ID 不存在则创建新的菜单。\f

    :param body: 包含菜单信息的 <AuthEditMenuRequest> 对象
    :return: 包含更新后菜单信息的 <ResponseModel> 对象
    """
    menu = await edit_menu(menu_id=body.id, name=body.name, identifier=body.identifier, node_id=body.nodeId)
    return ResponseModel(data=menu)


@router.delete("/menu/delete")
async def menu_delete(body: DeleteRequestModel) -> ResponseModel[MenuInfoResponse]:
    """
    删除权限菜单接口

    根据菜单 ID 删除指定的权限菜单。\f

    :param body: 包含菜单 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除菜单信息的 <ResponseModel> 对象
    """
    menu = await delete_menu(menu_id=body.id)
    return ResponseModel(data=menu)


@router.put("/role/edit")
async def role_edit(body: AuthEditRoleRequest) -> ResponseModel[RoleInfoResponse]:
    """
    添加或更新角色信息接口

    根据提供的角色 ID 更新角色信息，如果 ID 不存在则创建新的角色。\f

    :param body: 包含角色信息的 <AuthEditRoleRequest> 对象
    :return: 无内容的 <ResponseModel> 对象
    """
    role = await edit_role(
        role_id=body.id,
        name=body.name,
        describe=body.describe,
        identifier_list=body.menuIdentifierList,
    )
    return ResponseModel(data=role)


@router.post("/role/list")
async def role_list(
    body: AuthGetRoleListRequest,
) -> ResponseModel[list[RoleInfoResponse]]:
    """
    获取角色列表接口

    获取角色的分页列表，并可以通过关键字进行过滤。\f

    :param body: 包含分页和关键字信息的 <AuthGetRoleListRequest> 对象
    :return: 包含角色列表的 <ResponseModel> 对象
    """
    role = await get_role_list(body.page, body.pageSize, keyword=body.keyword)
    return ResponseModel(data=role)


@router.delete("/role/delete")
async def role_delete(body: DeleteRequestModel) -> ResponseModel[RoleInfoResponse]:
    """
    删除角色信息接口

    根据角色 ID 删除指定的角色信息。\f

    :param body: 包含角色 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除角色信息的 <ResponseModel> 对象
    """
    role = await delete_role(role_id=body.id)
    return ResponseModel(data=role)


@router.put("/affiliation/edit")
async def affiliation_edit(
    body: AuthEditAffiliationRequest,
) -> ResponseModel[AffiliationInfoResponse]:
    """
    添加或更新所属关系信息接口

    根据提供的所属关系 ID 更新所属关系信息，如果 ID 不存在则创建新的所属关系。\f

    :param body: 包含所属关系信息的 <AuthEditAffiliationRequest> 对象
    :return: 包含更新后所属关系信息的 <ResponseModel> 对象
    """
    affiliation = await edit_affiliation(affiliation_id=body.id, name=body.name, node_id=body.nodeId)
    return ResponseModel(data=affiliation)


@router.post("/affiliation/list")
async def affiliation_list(
    body: AuthGetAffiliationListRequest,
) -> ResponseModel[list[AffiliationListResponse]]:
    """
    获取所属关系列表接口

    获取指定节点的所有所属关系，并可以通过关键字进行过滤。\f

    :param body: 包含节点 ID 和关键字的 <AuthGetAffiliationListRequest> 对象
    :return: 包含所属关系列表的 <ResponseModel> 对象
    """
    affiliation = await get_affiliation_tree(node_id=body.nodeId, keyword=body.keyword)
    return ResponseModel(data=affiliation)


@router.delete("/affiliation/delete")
async def affiliation_delete(
    body: DeleteRequestModel,
) -> ResponseModel[AffiliationInfoResponse]:
    """
    删除所属关系接口

    根据所属关系 ID 删除指定的所属关系。\f

    :param body: 包含所属关系 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除所属关系信息的 <ResponseModel> 对象
    """
    affiliation = await delete_affiliation(affiliation_id=body.id)
    return ResponseModel(data=affiliation)


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
