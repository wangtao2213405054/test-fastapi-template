# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.auth.jwt import parse_jwt_user_data
from src.api.auth.service import get_current_user_table
from src.api.manage.models import UserTable
from src.models.types import ResponseModel

from .models import RouteListResponse
from .service import get_constant_route_tree, get_user_route_tree

router = APIRouter(prefix="/route", dependencies=[Depends(parse_jwt_user_data)])


@router.get("getConstantRoutes")
async def get_constant_routes() -> ResponseModel[list[RouteListResponse]]:
    """
    获取常量路由。 \f

    :return:
    """

    routes = await get_constant_route_tree()

    return ResponseModel(data=routes)


@router.get("getUserRoutes")
async def get_user_routes(
    user: Annotated[UserTable, Depends(get_current_user_table)],
) -> ResponseModel[list[RouteListResponse]]:
    """
    获取当前用户路由。 \f

    :param user: 当前用户信息
    :return:
    """

    routes = await get_user_route_tree(user=user)

    return ResponseModel(data=routes)
