import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style

from models.users import Users
from configs import AuthConfig

# 令对应当前页面的回调函数子模块生效
import callbacks.core_pages_c.users_man_c  # noqa: F401


def render():
    """子页面：系统管理-用户管理"""

    return [
        # 稳定触发初始化数据加载
        fuc.FefferyTimeout(id="core-users-table-init-data-trigger", delay=0),
        fac.AntdSpace(
            [
                fac.AntdBreadcrumb(
                    items=[
                        {"title": "系统管理"},
                        {"title": "用户管理"},
                    ]
                ),
                fac.AntdSpin(
                    fac.AntdTable(
                        id="core-users-table",
                        columns=[
                            {
                                "dataIndex": "user_id",
                                "title": "用户id",
                            },
                            {
                                "dataIndex": "user_name",
                                "title": "用户名",
                            },
                            {
                                "dataIndex": "user_role",
                                "title": "用户角色",
                                "renderOptions": {"renderType": "tags"},
                            },
                            {
                                "dataIndex": "编辑",
                                "title": "编辑",
                                "renderOptions": {
                                    "renderType": "button"
                                },
                            },
                            {
                                "dataIndex": "删除",
                                "title": "删除",
                                "renderOptions": {
                                    "renderType": "button",
                                    "renderButtonPopConfirmProps": {
                                        "title": "确认删除",
                                        "okText": "确定",
                                        "cancelText": "取消"
                                    }
                                },
                            },
                        ],
                        pagination={
                            "current": 1,
                            "total": len(Users.get_all_users()),  # 获取用户总数
                            "pageSize": 10,
                            "showSizeChanger": False,
                        },
                        mode="server-side",  # 使用服务端数据分页模式
                        bordered=True,
                        tableLayout="fixed",
                        rowSelectionType="checkbox",
                        sortOptions={
                            "sortDataIndexes": [
                                "user_id",
                                "user_name",
                                "user_role",
                            ],
                        },
                        filterOptions={
                            "user_name": {
                                "filterMode": "keyword",
                            },
                            "user_role": {
                                "filterMode": "checkbox",
                            },
                        },
                        title=fac.AntdSpace(
                            [
                                fac.AntdButton(
                                    "刷新",
                                    id="core-users-refresh-data",
                                    color="primary",
                                    variant="filled",
                                ),
                                fac.AntdButton(
                                    "添加用户",
                                    id="core-users-add-user",
                                    color="primary",
                                    variant="filled",
                                ),
                                fac.AntdPopconfirm(
                                    fac.AntdButton(
                                        "删除选中",
                                        id="core-users-delete-selected",
                                        color="danger",
                                        variant="filled",
                                    ),
                                    id="core-users-delete-selected-confirm",
                                    title="删除用户",
                                    description="删除已选中用户，请谨慎操作",
                                ),
                            ],
                            size=3,
                        ),
                    ),
                    delay=300,
                ),
                # 添加用户模态框
                fac.AntdDrawer(
                    id="core-users-add-modal",
                    title=fac.AntdSpace([fac.AntdIcon(icon="antd-user-add"), "添加用户"]),
                    mask=False,
                    placement='right',
                    width="40vw",
                    maskClosable=False,
                    visible=False,
                ),
                # 编辑用户模态框
                fac.AntdDrawer(
                    id="core-users-edit-modal",
                    title=fac.AntdSpace([fac.AntdIcon(icon="antd-user"), "编辑用户"]),
                    mask=False,
                    placement='right',
                    width="40vw",
                    maskClosable=False,
                    visible=False,
                ),
            ],
            direction="vertical",
            style=style(width="100%"),
        ),
    ]