# _author: Coke
# _date: 2024/7/25 14:15
# _description: 用户验证相关路由

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.models.types import DeleteRequestModel, ResponseModel
from src.websocketio import socket

from .jwt import parse_jwt_user_data
from .models.models import (
    AffiliationInfoResponse,
    AffiliationListResponse,
    MenuInfoResponse,
    MenuListResponse,
    RoleInfoResponse,
    UserResponse,
)
from .models.types import (
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

router = APIRouter(prefix="/auth", dependencies=[Depends(parse_jwt_user_data)])


@router.post("/user/create")
async def user_edit(body: CreateUserRequest) -> ResponseModel[UserResponse]:
    """
    创建用户接口\f

    :param body: <CreateUserRequest> 对象
    :return:
    """
    user = await create_user(
        name=body.name, email=body.email, mobile=body.mobile, password=body.password, affiliation_id=body.affiliationId
    )

    return ResponseModel(data=user)


@router.post("/user/update")
async def user_update(body: UpdateUserInfoRequest) -> ResponseModel[UserResponse]:
    """
    修改用户信息\f

    :param body: <UpdateUserInfoRequest> 对象
    :return:
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
    修改用户密码\f

    :param body: <UpdatePasswordRequest> 对象
    :return:
    """

    await update_password(user_id=body.id, old_password=body.oldPassword, new_password=body.newPassword)
    return ResponseModel()


@router.get("/user/info")
async def user_info(user: Annotated[UserResponse, Depends(get_current_user)]) -> ResponseModel[UserResponse]:
    """
    获取当前用户信息\f

    :param user: 用户信息
    :return:
    """

    return ResponseModel(data=user)


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
    menu = await edit_menu(menu_id=body.id, name=body.name, identifier=body.identifier, node_id=body.nodeId)
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
        role_id=body.id, name=body.name, identifier=body.identifier, identifier_list=body.menuIdentifierList
    )

    return ResponseModel()


@router.post("/role/list")
async def role_list(body: AuthGetRoleListRequest) -> ResponseModel[list[RoleInfoResponse]]:
    """
    获取角色列表\f

    :param body: <AuthGetRoleListRequest> 对象
    :return:
    """
    role = await get_role_list(body.page, body.pageSize, keyword=body.keyword)

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
    print(token, "token")
    print(socket.rooms(sid), "rooms")
    # if not token:
    #     return False


@socket.event
def disconnect(sid: str):
    """
    socketio 断连事件

    :return:
    """
    print(sid, "123")
