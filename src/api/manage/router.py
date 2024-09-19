# _author: Coke
# _date: 2024/7/25 14:15
# _description: 系统管理相关路由


from fastapi import APIRouter, Depends

from src.api.auth.jwt import validate_permission
from src.models.types import BatchDeleteRequestModel, DeleteRequestModel, Pagination, ResponseModel

from .models import (
    AffiliationInfoResponse,
    AffiliationListResponse,
    MenuInfoResponse,
    MenuListResponse,
    MenuPermissionTreeResponse,
    MenuSimplifyListResponse,
    RoleInfoResponse,
    UserResponse,
)
from .service import (
    batch_delete_menu,
    batch_delete_role,
    create_user,
    delete_affiliation,
    delete_menu,
    delete_role,
    edit_affiliation,
    edit_menu,
    edit_role,
    edit_role_permission,
    get_affiliation_tree,
    get_menu_permission_tree,
    get_menu_simplify_tree,
    get_menu_tree,
    get_page_list,
    get_role_list,
    update_password,
    update_user,
)
from .types import (
    AuthEditAffiliationRequest,
    AuthEditRoleRequest,
    AuthGetAffiliationListRequest,
    AuthGetRoleListRequest,
    CreateUserRequest,
    ManageEditMenuRequest,
    ManageEditRolePermissionRequest,
    ManageGetDetailPermissionRequest,
    ManageGetMenuListRequest,
    UpdatePasswordRequest,
    UpdateUserInfoRequest,
)

router = APIRouter(prefix="/manage", dependencies=[Depends(validate_permission)])


@router.post("/createUser")
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
        role_id=body.roleId,
        avatar=body.avatarUrl.unicode_string() if body.avatarUrl else None,
    )
    return ResponseModel(data=user)


@router.post("/updateUserInfo")
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


@router.post("/updateUserPassword")
async def user_update_password(body: UpdatePasswordRequest) -> ResponseModel:
    """
    修改用户密码接口

    更新用户的密码。需要提供用户 ID、旧密码和新密码。\f

    :param body: 包含密码信息的 <UpdatePasswordRequest> 对象
    :return: 无内容的 <ResponseModel> 对象
    """
    await update_password(user_id=body.id, old_password=body.oldPassword, new_password=body.newPassword)
    return ResponseModel()


@router.put("/editRoleInfo")
async def role_edit(body: AuthEditRoleRequest) -> ResponseModel[RoleInfoResponse]:
    """
    添加或更新角色信息接口

    根据提供的角色 ID 更新角色信息，如果 ID 不存在则创建新的角色。\f

    :param body: 包含角色信息的 <AuthEditRoleRequest> 对象
    :return: 更新后的 <RoleInfoResponse> 对象
    """
    role = await edit_role(
        role_id=body.id,
        name=body.name,
        describe=body.describe,
        status=body.status,
    )
    return ResponseModel(data=role)


@router.put("/updateRolePermission")
async def role_permission(body: ManageEditRolePermissionRequest) -> ResponseModel[RoleInfoResponse]:
    """
    更新当前角色的权限信息

    根据提供的角色 ID 更新角色的路由、按钮、接口权限信息。\f
    :param body: 包含角色信息的 <ManageEditRolePermissionRequest> 对象
    :return: 更新后的 <RoleInfoResponse> 对象
    """

    role = await edit_role_permission(
        role_id=body.id,
        menu_ids=body.menuIds,
        interface_codes=body.interfaceCodes,
        button_codes=body.buttonCodes,
    )
    return ResponseModel(data=role)


@router.post("/getRoleList")
async def role_list(
    body: AuthGetRoleListRequest,
) -> ResponseModel[Pagination[list[RoleInfoResponse]]]:
    """
    获取角色列表接口

    获取角色的分页列表，并可以通过关键字进行过滤。\f

    :param body: 包含分页和关键字信息的 <AuthGetRoleListRequest> 对象
    :return: 包含角色列表的 <ResponseModel> 对象
    """
    role = await get_role_list(body.page, body.pageSize, keyword=body.keyword, status=body.status)
    return ResponseModel(data=role)


@router.delete("/deleteRole")
async def role_delete(body: DeleteRequestModel) -> ResponseModel[RoleInfoResponse]:
    """
    删除角色信息接口

    根据角色 ID 删除指定的角色信息。\f

    :param body: 包含角色 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除角色信息的 <ResponseModel> 对象
    """
    role = await delete_role(role_id=body.id)
    return ResponseModel(data=role)


@router.delete("/batchDeleteRole")
async def role_batch_delete(body: BatchDeleteRequestModel) -> ResponseModel[list[RoleInfoResponse]]:
    """
    批量删除角色接口

    根据角色 ID 列表删除指定的角色。\f

    :param body: 包含菜单 ids 的 <DeleteRequestModel> 对象
    :return:
    """

    role = await batch_delete_role(ids=body.ids)
    return ResponseModel(data=role)


@router.put("/editAffiliationInfo")
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


@router.post("/getAffiliationList")
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


@router.delete("/deleteAffiliation")
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


@router.post("/getMenuList")
async def menu_list(body: ManageGetMenuListRequest) -> ResponseModel[Pagination[list[MenuListResponse]]]:
    """
    获取菜单列表接口

    获取指定节点的所有菜单，并可以通过关键字进行过滤。\f

    :param body: 包含节点 ID 和关键字的 <ManageGetMenuListRequest> 对象
    :return: 包含菜单列表的 <ResponseModel> 对象
    """

    menu = await get_menu_tree(node_id=body.nodeId, keyword=body.keyword, page=body.page, size=body.pageSize)
    return ResponseModel(data=menu)


@router.put("/editMenuInfo")
async def menu_edit(body: ManageEditMenuRequest) -> ResponseModel[MenuInfoResponse]:
    """
    新增/修改 路由菜单接口

    根据提供的菜单 ID 更新菜单信息，如果 ID 不存在则创建新的菜单。\f

    :param body: <ManageEditMenuRequest> 对象
    :return: 包含菜单列表的 <ResponseModel> 对象
    """

    menu = await edit_menu(
        menu_id=body.id,
        component=body.component,
        node_id=body.nodeId,
        menu_name=body.menuName,
        menu_type=body.menuType,
        route_name=body.routeName,
        route_path=body.routePath,
        i18n_key=body.i18nKey,
        order=body.order,
        icon_type=body.iconType,
        icon=body.icon,
        status=body.status,
        hide_in_menu=body.hideInMenu,
        multi_tab=body.multiTab,
        keep_alive=body.keepAlive,
        href=body.href.unicode_string() if body.href else None,
        constant=body.constant,
        fixed_index_in_tab=body.fixedIndexInTab,
        homepage=body.homepage,
        query=body.query,
        buttons=body.buttons,
        interfaces=body.interfaces,
    )
    return ResponseModel(data=menu)


@router.delete("/deleteMenu")
async def menu_delete(body: DeleteRequestModel) -> ResponseModel[list[MenuInfoResponse]]:
    """
    删除菜单接口

    根据菜单 ID 删除指定的菜单。\f

    :param body: 包含菜单 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除菜单信息的 <ResponseModel> 对象
    """

    menu = await delete_menu(menu_id=body.id)
    return ResponseModel(data=menu)


@router.delete("/batchDeleteMenu")
async def menu_batch_delete(body: BatchDeleteRequestModel) -> ResponseModel[list[MenuInfoResponse]]:
    """
    批量删除菜单接口

    根据菜单 ID 列表删除指定的菜单。\f

    :param body: 包含菜单 ids 的 <DeleteRequestModel> 对象
    :return:
    """

    menu = await batch_delete_menu(menu_ids=body.ids)
    return ResponseModel(data=menu)


@router.get("/getPageAll")
async def page_all() -> ResponseModel[list[str]]:
    """
    获取当前所有的页面\f

    :return:
    """
    page = await get_page_list()

    return ResponseModel(data=page)


@router.get("/getRouterMenuAll")
async def router_menu_all() -> ResponseModel[list[MenuSimplifyListResponse]]:
    """
    获取简化后的路由菜单列表。\f

    :return: 简化后的菜单列表
    """
    menu = await get_menu_simplify_tree()

    return ResponseModel(data=menu)


@router.post("/getPermissionMenuAll")
async def buttons_menu_all(params: ManageGetDetailPermissionRequest) -> ResponseModel[list[MenuPermissionTreeResponse]]:
    """
    通过菜单类型获取对应的列表, 支持 buttons or interfaces 参数。\f

    :param params: <ManageGetDetailPermissionRequest>
    :return: 对应菜单类型的列表
    """
    menu = await get_menu_permission_tree(params.menuType)

    return ResponseModel(data=menu)
