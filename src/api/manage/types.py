# _author: Coke
# _date: 2024/8/22 下午5:00
# _description:

from fastapi import Body
from src.models.types import CustomModel


# 菜单类型
MENU_DIRECTORY = 1  # 目录
MENU_ROUTE = 2  # 路由
MENU_BUTTON = 3  # 按钮
MENU_INTERFACE = 4  # 接口

# Icon 类型
ICONIFY_ICON = 1
LOCAL_ICON = 2


class ManageEditMenuRequest(CustomModel):
    """修改权限菜单请求"""

    id: int = Body(0, description="菜单ID")
    nodeId: int = Body(0, description="节点ID")
    name: str = Body(..., description="菜单名称")
    menuType: str = Body(..., description="菜单类型")
    routeName: str = Body(..., description="路由名称")
    routePath: str = Body(..., description="路由路径")
    i18nKey: str = Body(None, description="国际化Key")
    order: int = Body(1, description="排序")
    iconType: int = Body(..., description="icon类型")
    icon: str = Body(..., description="icon 地址")
    status: bool = Body(True, description="菜单状态")
    hidden: bool = Body(False, description="隐藏菜单")
    multiTab: bool = Body(False, description="是否支持多标签页")
    keepAlive: bool = Body(False, description="缓存路由")
    href: str = Body(None, description="外链地址")
