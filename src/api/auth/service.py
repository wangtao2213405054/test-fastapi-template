
from datetime import datetime, timedelta
from typing import Any, List

from pydantic import UUID4
from sqlmodel import select, or_

from src import utils
from .config import auth_config
from .models.models import (
    MenuTable, MenuCreate, MenuListResponse, MenuInfoResponse,
    RoleTable, RoleCreate, RoleInfoResponse,
    AffiliationTable, AffiliationCreate, AffiliationListResponse, AffiliationInfoResponse
)
from src.database import (
    execute, fetch_one, insert_one, fetch_all, update_one, select_one,
    fetch_page, delete_one, like
)

import uuid


async def edit_affiliation(*, affiliation_id: int, name: str, node_id: int) -> AffiliationInfoResponse:
    """
    创建/更新 一个所属关系
    :param affiliation_id: 所属关系ID 如何为真则视为修改
    :param name: 所属关系名称
    :param node_id: 节点ID
    :return:
    """
    if affiliation_id:
        affiliation: AffiliationInfoResponse = await select_one(
            select(AffiliationTable).where(AffiliationTable.id == affiliation_id)
        )
        affiliation.name = name
        affiliation.nodeId = node_id
        return await update_one(affiliation)

    return await insert_one(AffiliationTable, AffiliationCreate(name=name, nodeId=node_id))


async def delete_affiliation(*, affiliation_id) -> AffiliationInfoResponse:
    """
    删除一个所属关系
    :param affiliation_id: 所属关系ID
    :return:
    """
    return await delete_one(select(AffiliationTable).where(AffiliationTable.id == affiliation_id))


async def get_affiliation_tree(*, node_id: int, keyword: str = "") -> List[AffiliationListResponse]:
    """
    获取当前的所属关系树
    :param node_id: 节点ID
    :param keyword: 关键字查询
    :return:
    """
    affiliation_dict_list: List[AffiliationListResponse] = []

    affiliation_list: List[AffiliationInfoResponse] = await fetch_all(
        select(AffiliationTable).where(
            AffiliationTable.nodeId == node_id,
            like(field=AffiliationTable.name, keyword=keyword)
        )
    )

    for item in affiliation_list:
        children = await get_affiliation_tree(node_id=item.id)
        items = AffiliationListResponse(children=children, **item.model_dump())
        affiliation_dict_list.append(items)

    return affiliation_dict_list


async def edit_menu(*, menu_id: int, name: str, identifier: str, node_id: int) -> MenuInfoResponse:
    """
    创建/更新 一个权限菜单
    :param menu_id: 权限菜单ID 如何为真则视为修改
    :param name: 菜单名称
    :param identifier: 菜单标识符
    :param node_id: 节点ID
    :return:
    """
    # 修改
    if menu_id:
        menu: MenuInfoResponse = await select_one(select(MenuTable).where(MenuTable.id == menu_id))
        menu.name = name
        menu.identifier = identifier
        menu.nodeId = node_id
        return await update_one(menu)

    return await insert_one(MenuTable, MenuCreate(name=name, identifier=identifier, nodeId=node_id))


async def delete_menu(*, menu_id: int) -> MenuInfoResponse:
    """
    删除一个权限菜单
    :param menu_id: 权限菜单ID
    :return:
    """
    return await delete_one(select(MenuTable).where(MenuTable.id == menu_id))


async def get_menu_tree(*, node_id: int, keyword: str = "") -> List[MenuListResponse]:
    """
    递归遍历所有子菜单信息
    :param node_id: 开始节点
    :param keyword: 关键字匹配
    :return:
    """
    menu_dict_list: List[MenuListResponse] = []

    menu_list: List[MenuInfoResponse] = await fetch_all(
        select(MenuTable).where(
            MenuTable.nodeId == node_id,
            or_(like(field=MenuTable.name, keyword=keyword), like(field=MenuTable.identifier, keyword=keyword))
        )
    )

    for item in menu_list:
        children = await get_menu_tree(node_id=item.id)
        items = MenuListResponse(children=children, **item.model_dump())
        menu_dict_list.append(items)

    return menu_dict_list


async def edit_role(*, role_id: int, name: str, identifier: str, identifier_list: List[str]) -> RoleInfoResponse:
    """
    创建/修改 一个角色信息
    :param role_id: 角色ID
    :param name: 角色名称
    :param identifier: 角色标识符
    :param identifier_list: 此角色绑定的权限菜单
    :return:
    """

    if role_id:
        role: RoleInfoResponse = await select_one(select(RoleTable).where(RoleTable.id == role_id))
        role.name = name
        role.identifier = identifier
        role.identifierList = identifier_list
        return await update_one(role)

    return await insert_one(RoleTable, RoleCreate(name=name, identifier=identifier, identifier_list=identifier_list))


async def get_role_list(page: int, size: int, *, keyword: str = "") -> List[RoleInfoResponse]:
    """
    获取角色信息列表
    :param page: 当前页
    :param size: 当前页大小
    :param keyword: 关键字查询, name or identifier
    :return:
    """

    print(keyword, type(keyword))
    return await fetch_page(
        select(RoleTable).where(
            or_(like(field=RoleTable.name, keyword=keyword), like(field=RoleTable.identifier, keyword=keyword))
        ),
        page=page,
        size=size
    )


async def delete_role(*, role_id: int) -> RoleInfoResponse:
    """
    删除一个角色信息
    :param role_id: 角色信息ID
    :return:
    """

    return await delete_one(select(RoleTable).where(RoleTable.id == role_id))


# async def create_user(user: AuthUser) -> dict[str, Any] | None:
#     insert_query = (
#         insert(auth_user)
#         .values(
#             {
#                 "email": user.email,
#                 "password": hash_password(user.password),
#                 "created_at": datetime.now(),
#             }
#         )
#         .returning(auth_user)
#     )
#
#     return await fetch_one(insert_query)


async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    select_query = select(auth_user).where(auth_user.c.id == user_id)

    return await fetch_one(select_query)


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    select_query = select(auth_user).where(auth_user.c.email == email)

    return await fetch_one(select_query)


async def create_refresh_token(
        *, user_id: int, refresh_token: str | None = None
) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    insert_query = refresh_tokens.insert().values(
        uuid=uuid.uuid4(),
        refresh_token=refresh_token,
        expires_at=datetime.now() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        user_id=user_id,
    )
    await execute(insert_query)

    return refresh_token


async def get_refresh_token(refresh_token: str) -> dict[str, Any] | None:
    select_query = refresh_tokens.select().where(
        refresh_tokens.c.refresh_token == refresh_token
    )

    return await fetch_one(select_query)


async def expire_refresh_token(refresh_token_uuid: UUID4) -> None:
    update_query = (
        refresh_tokens.update()
        .values(expires_at=datetime.now() - timedelta(days=1))
        .where(refresh_tokens.c.uuid == refresh_token_uuid)
    )

    await execute(update_query)

# async def authenticate_user(auth_data: AuthUser) -> dict[str, Any]:
#     user = await get_user_by_email(auth_data.email)
#     if not user:
#         raise InvalidCredentials()
#
#     if not check_password(auth_data.password, user["password"]):
#         raise InvalidCredentials()
#
#     return user
