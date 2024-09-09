# _author: Coke
# _date: 2024/8/26 下午3:51
# _description: 系统管理相关路由

from fastapi import APIRouter, Depends

from src.api.auth.jwt import validate_permission
from src.models.types import BatchDeleteRequestModel, DeleteRequestModel, Pagination, ResponseModel

from .models import MenuInfoResponse, MenuListResponse
from .service import batch_delete_menu, delete_menu, edit_menu, get_menu_tree, get_page_list
from .types import ManageEditMenuRequest, ManageGetMenuListRequest

router = APIRouter(prefix="/manage", dependencies=[Depends(validate_permission)])


@router.post("/menu/list")
async def menu_list(body: ManageGetMenuListRequest) -> ResponseModel[Pagination[list[MenuListResponse]]]:
    """
    获取菜单列表接口

    获取指定节点的所有菜单，并可以通过关键字进行过滤。\f

    :param body: 包含节点 ID 和关键字的 <ManageGetMenuListRequest> 对象
    :return: 包含菜单列表的 <ResponseModel> 对象
    """

    menu = await get_menu_tree(node_id=body.nodeId, keyword=body.keyword, page=body.page, size=body.pageSize)
    return ResponseModel(data=menu)


@router.put("/menu/edit")
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


@router.delete("/menu/delete")
async def menu_delete(body: DeleteRequestModel) -> ResponseModel[list[MenuInfoResponse]]:
    """
    删除菜单接口

    根据菜单 ID 删除指定的菜单。\f

    :param body: 包含菜单 ID 的 <DeleteRequestModel> 对象
    :return: 包含被删除菜单信息的 <ResponseModel> 对象
    """

    menu = await delete_menu(menu_id=body.id)
    return ResponseModel(data=menu)


@router.delete("/menu/batch/delete")
async def menu_batch_delete(body: BatchDeleteRequestModel) -> ResponseModel[list[MenuInfoResponse]]:
    """
    批量删除菜单接口

    根据菜单 ID 列表删除指定的菜单。\f

    :param body: 包含菜单 ids 的 <DeleteRequestModel> 对象
    :return:
    """

    menu = await batch_delete_menu(menu_ids=body.ids)
    return ResponseModel(data=menu)


@router.get("/page/all")
async def page_all() -> ResponseModel[list[str]]:
    """
    获取当前所有的页面\f

    :return:
    """
    page = await get_page_list()

    return ResponseModel(data=page)
