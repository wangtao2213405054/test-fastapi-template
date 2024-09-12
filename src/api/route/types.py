# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from fastapi import Body

from src.models.types import CustomModel


class GetRouteIsExistRequest(CustomModel):
    """查询此路由是否存在"""

    routeName: str = Body(..., description="路由路径")
