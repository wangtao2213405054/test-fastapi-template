import uuid
from datetime import datetime, timedelta
from typing import Any

from pydantic import UUID4
from sqlmodel import col, select, insert, or_

from src import utils
from src.auth.config import auth_config
from src.auth.exceptions import InvalidCredentials
from src.auth.security import check_password, hash_password
from src.auth.models import MenuTable, MenuCreate, MenuListResponse, MenuInfoResponse
from src.database import execute, fetch_one, insert_one, fetch_all, update_one


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
        menu: MenuInfoResponse = await fetch_one(select(MenuTable).where(MenuTable.id == menu_id))
        menu.name = name
        menu.identifier = identifier
        menu.nodeId = node_id
        return await update_one(menu)

    return await insert_one(MenuTable, MenuCreate(name=name, identifier=identifier, nodeId=node_id))


async def get_menu_tree(node_id: int, keyword: str = "") -> list[MenuListResponse]:
    """
    递归遍历所有子菜单信息
    :param node_id: 开始节点
    :param keyword: 关键字匹配
    :return:
    """
    menu_dict_list: list[MenuListResponse] = []

    menu_list: list[MenuTable] = await fetch_all(
        select(MenuTable).where(
            MenuTable.nodeId == node_id,
            or_(col(MenuTable.name).like(f'%{keyword}%'), col(MenuTable.identifier).like(f'%{keyword}%'))
        )
    )

    for item in menu_list:
        children = await get_menu_tree(item.id)
        items = MenuListResponse(children=children, **item.model_dump())
        menu_dict_list.append(items)

    return menu_dict_list


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
