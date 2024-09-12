# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from src.api.manage.models import RouteBase


class RouteListResponse(RouteBase):
    """路由列表响应实例"""

    id: int
    children: list["RouteListResponse"] = []
