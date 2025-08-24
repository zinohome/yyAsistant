import uuid
import time
import dash
from dash import set_props
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State
from werkzeug.security import generate_password_hash

from server import app
from models.users import Users
from configs import AuthConfig


def refresh_users_table_data():
    """刷新用户表格数据"""

    # 查询全部用户信息
    all_users = Users.get_all_users()

    return [
        {
            "user_id": item["user_id"],
            "user_name": item["user_name"],
            "user_role": {
                "tag": AuthConfig.roles.get(item["user_role"])["description"],
                "color": (
                    "gold" if item["user_role"] == AuthConfig.admin_role else "blue"
                ),
            },
            "操作": [
                {
                    "content": "编辑",
                    "type": "link",
                    "disabled": item["user_role"] == AuthConfig.admin_role and len(all_users) <= 1,
                },
                {
                    "content": "删除",
                    "type": "link",
                    "danger": True,
                    "disabled": item["user_role"] == AuthConfig.admin_role and len(all_users) <= 1,
                },
            ],
            "key": item["user_id"],
        }
        for item in all_users
    ]


@app.callback(
    Output("core-users-table", "data"),
    [
        Input("core-users-table-init-data-trigger", "timeoutCount"),
        Input("core-users-table", "pagination"),
        Input("core-users-table", "sorter"),
        Input("core-users-table", "filter"),
    ],
    prevent_initial_call=True,
)
def handle_users_table_data_load(timeoutCount, pagination, sorter, _filter):
    """处理用户表数据加载"""

    # 为本次查询构造查询条件
    query_condition = {}

    # 若存在有效排序条件
    if sorter and sorter["columns"]:
        sort_column = sorter["columns"][0]
        sort_order = sorter["orders"][0]
        # 映射前端列名到模型字段名
        if sort_column == "user_name":
            query_condition["order_by"] = "user_name"
            query_condition["order"] = sort_order
        elif sort_column == "user_role":
            query_condition["order_by"] = "user_role"
            query_condition["order"] = sort_order

    # 若存在有效筛选条件
    if _filter:
        if _filter.get("user_name"):
            query_condition["user_name_keyword"] = _filter["user_name"][0]
        if _filter.get("user_role"):
            query_condition["user_role"] = _filter["user_role"]

    # 获取用户数据
    all_users = Users.get_all_users()

    # 应用排序
    if query_condition.get("order_by") and query_condition.get("order"):
        order_by = query_condition["order_by"]
        order = query_condition["order"]
        all_users.sort(
            key=lambda x: x[order_by],
            reverse=(order == "descend")
        )

    # 应用筛选
    if query_condition.get("user_name_keyword"):
        keyword = query_condition["user_name_keyword"].lower()
        all_users = [user for user in all_users if keyword in user["user_name"].lower()]

    if query_condition.get("user_role"):
        roles = query_condition["user_role"]
        all_users = [user for user in all_users if user["user_role"] in roles]

    # 应用分页
    start_index = (pagination["current"] - 1) * pagination["pageSize"]
    end_index = start_index + pagination["pageSize"]
    paginated_users = all_users[start_index:end_index]

    return [
        {
            "user_id": item["user_id"],
            "user_name": item["user_name"],
            "user_role": {
                "tag": AuthConfig.roles.get(item["user_role"])["description"],
                "color": (
                    "gold" if item["user_role"] == AuthConfig.admin_role else "blue"
                ),
            },
            "操作": [
                {
                    "content": "编辑",
                    "type": "link",
                    "disabled": item["user_role"] == AuthConfig.admin_role and len(all_users) <= 1,
                },
                {
                    "content": "删除",
                    "type": "link",
                    "danger": True,
                    "disabled": item["user_role"] == AuthConfig.admin_role and len(all_users) <= 1,
                },
            ],
            "key": item["user_id"],
        }
        for item in paginated_users
    ]


@app.callback(
    [
        Output("core-users-add-modal", "visible"),
        Output("core-users-add-modal", "children"),
    ],
    Input("core-users-add-user", "nClicks"),
    prevent_initial_call=True,
)
def open_add_user_modal(nClicks):
    """打开添加用户模态框"""

    return [
        True,
        fac.AntdForm(
            [
                fac.AntdFormItem(
                    fac.AntdInput(
                        id="core-users-add-form-user-name",
                        placeholder="请输入用户名",
                        allowClear=True,
                    ),
                    label="用户名",
                ),
                fac.AntdFormItem(
                    fac.AntdInput(
                        id="core-users-add-form-user-password",
                        placeholder="请输入密码",
                        mode="password",
                        allowClear=True,
                    ),
                    label="密码",
                ),
                fac.AntdFormItem(
                    fac.AntdSelect(
                        id="core-users-add-form-user-role",
                        options=[
                            {"label": value["description"], "value": key}
                            for key, value in AuthConfig.roles.items()
                        ],
                        allowClear=False,
                    ),
                    label="用户角色",
                ),
            ],
            id="core-users-add-form",
            key=str(uuid.uuid4()),  # 强制刷新
            enableBatchControl=True,
            layout="vertical",
            values={"core-users-add-form-user-role": AuthConfig.normal_role},
            style=style(marginTop=32),
        ),
    ]


@app.callback(
    Input("core-users-add-modal", "okCounts"),
    [State("core-users-add-form", "values")],
    prevent_initial_call=True,
)
def handle_add_user(okCounts, values):
    """处理添加用户逻辑"""

    # 获取表单数据
    values = values or {}

    # 检查表单数据完整性
    if not (
        values.get("core-users-add-form-user-name")
        and values.get("core-users-add-form-user-password")
    ):
        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    type="error",
                    content="请完善用户信息后再提交",
                )
            },
        )
    else:
        # 检查用户名是否重复
        match_user = Users.get_user_by_name(
            values["core-users-add-form-user-name"]
        )

        # 若用户名重复
        if match_user:
            set_props(
                "global-message",
                {
                    "children": fac.AntdMessage(
                        type="error",
                        content="用户名已存在",
                    )
                },
            )
        else:
            # 添加用户
            Users.add_user(
                user_id=str(uuid.uuid4()),
                user_name=values["core-users-add-form-user-name"],
                password_hash=generate_password_hash(
                    values["core-users-add-form-user-password"]
                ),
                user_role=values["core-users-add-form-user-role"],
            )

            set_props(
                "global-message",
                {
                    "children": fac.AntdMessage(
                        type="success",
                        content="用户添加成功",
                    )
                },
            )

            # 关闭模态框
            set_props("core-users-add-modal", {"visible": False})

            # 刷新用户列表
            set_props(
                "core-users-table",
                {
                    # 重置分页参数
                    "pagination": {
                        "current": 1,
                        "total": len(Users.get_all_users()),  # 获取用户最新总数
                        "pageSize": 10,
                        "showSizeChanger": False,
                    },
                },
            )


@app.callback(
    [
        Output("core-users-edit-modal", "visible"),
        Output("core-users-edit-modal", "children"),
    ],
    Input("core-users-table", "nClicksButton"),
    [State("core-users-table", "clickedContent"),
     State("core-users-table", "recentlyButtonClickedRow")],
    prevent_initial_call=True,
)
def open_edit_user_modal(nClicksButton, clickedContent, recentlyButtonClickedRow):
    """打开编辑用户模态框"""

    if clickedContent == "编辑":
        user_id = recentlyButtonClickedRow["user_id"]
        user = Users.get_user(user_id)

        return [
            True,
            [
                # 存储当前编辑的用户ID
                fac.AntdHidden(id="core-users-edit-form-user-id", value=user_id),
                fac.AntdForm(
                    [
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id="core-users-edit-form-user-name",
                                placeholder="请输入用户名",
                                value=user.user_name,
                                allowClear=True,
                            ),
                            label="用户名",
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id="core-users-edit-form-user-password",
                                placeholder="若不修改密码则留空",
                                mode="password",
                                allowClear=True,
                            ),
                            label="密码",
                        ),
                        fac.AntdFormItem(
                            fac.AntdSelect(
                                id="core-users-edit-form-user-role",
                                options=[
                                    {"label": value["description"], "value": key}
                                    for key, value in AuthConfig.roles.items()
                                ],
                                value=user.user_role,
                                allowClear=False,
                            ),
                            label="用户角色",
                        ),
                    ],
                    id="core-users-edit-form",
                    key=str(uuid.uuid4()),  # 强制刷新
                    enableBatchControl=True,
                    layout="vertical",
                    style=style(marginTop=32),
                ),
            ],
        ]

    return dash.no_update


@app.callback(
    Input("core-users-edit-modal", "okCounts"),
    [
        State("core-users-edit-form-user-id", "value"),
        State("core-users-edit-form", "values"),
    ],
    prevent_initial_call=True,
)
def handle_edit_user(okCounts, user_id, values):
    """处理编辑用户逻辑"""

    # 获取表单数据
    values = values or {}

    # 检查用户名是否存在
    if values.get("core-users-edit-form-user-name"):
        existing_user = Users.get_user_by_name(values["core-users-edit-form-user-name"])
        if existing_user and existing_user.user_id != user_id:
            set_props(
                "global-message",
                {
                    "children": fac.AntdMessage(
                        type="error",
                        content="用户名已存在",
                    )
                },
            )
            return

    # 准备更新数据
    update_data = {}
    if values.get("core-users-edit-form-user-name"):
        update_data["user_name"] = values["core-users-edit-form-user-name"]
    if values.get("core-users-edit-form-user-password"):
        update_data["password_hash"] = generate_password_hash(values["core-users-edit-form-user-password"])
    if values.get("core-users-edit-form-user-role"):
        update_data["user_role"] = values["core-users-edit-form-user-role"]

    # 执行更新
    Users.update_user(user_id=user_id, **update_data)

    set_props(
        "global-message",
        {
            "children": fac.AntdMessage(
                type="success",
                content="用户更新成功",
            )
        },
    )

    # 关闭模态框
    set_props("core-users-edit-modal", {"visible": False})

    # 刷新用户列表
    set_props(
        "core-users-table",
        {"data": refresh_users_table_data()},
    )


@app.callback(
    Input("core-users-table", "nClicksButton"),
    [
        State("core-users-table", "clickedContent"),
        State("core-users-table", "recentlyButtonClickedRow"),
    ],
    prevent_initial_call=True,
)
def handle_delete_user(nClicksButton, clickedContent, recentlyButtonClickedRow):
    """处理删除用户逻辑"""

    if clickedContent == "删除":
        user_id = recentlyButtonClickedRow["user_id"]
        user = Users.get_user(user_id)

        # 防止删除最后一个管理员
        all_users = Users.get_all_users()
        admin_users = [u for u in all_users if u["user_role"] == AuthConfig.admin_role]
        if user.user_role == AuthConfig.admin_role and len(admin_users) <= 1:
            set_props(
                "global-message",
                {
                    "children": fac.AntdMessage(
                        type="warning",
                        content="不能删除最后一个管理员用户",
                    )
                },
            )
            return

        # 执行删除
        Users.delete_user(user_id=user_id)

        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    type="success",
                    content="用户删除成功",
                )
            },
        )

        # 刷新用户列表
        set_props(
            "core-users-table",
            {
                # 重置分页参数
                "pagination": {
                    "current": 1,
                    "total": len(Users.get_all_users()),  # 获取用户最新总数
                    "pageSize": 10,
                    "showSizeChanger": False,
                },
                "selectedRowKeys": [],
            },
        )


@app.callback(
    Input("core-users-delete-selected-confirm", "confirmCounts"),
    [State("core-users-table", "selectedRowKeys")],
    prevent_initial_call=True,
)
def handle_delete_selected_users(confirmCounts, selectedRowKeys):
    """处理删除选中用户逻辑"""

    if not selectedRowKeys:
        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    type="warning",
                    content="请先选择要删除的用户",
                )
            },
        )
        return

    # 检查是否包含最后一个管理员
    all_users = Users.get_all_users()
    admin_users = [u for u in all_users if u["user_role"] == AuthConfig.admin_role]
    selected_admin_users = [u for u in selectedRowKeys if any(au["user_id"] == u and au["user_role"] == AuthConfig.admin_role for au in all_users)]

    if len(admin_users) <= len(selected_admin_users):
        set_props(
            "global-message",
            {
                "children": fac.AntdMessage(
                    type="warning",
                    content="不能删除所有管理员用户",
                )
            },
        )
        return

    # 执行删除
    for user_id in selectedRowKeys:
        Users.delete_user(user_id=user_id)

    set_props(
        "global-message",
        {
            "children": fac.AntdMessage(
                type="success",
                content=f"成功删除 {len(selectedRowKeys)} 个用户",
            )
        },
    )

    # 刷新用户列表
    set_props(
        "core-users-table",
        {
            # 重置分页参数
            "pagination": {
                "current": 1,
                "total": len(Users.get_all_users()),  # 获取用户最新总数
                "pageSize": 10,
                "showSizeChanger": False,
            },
            "selectedRowKeys": [],
        },
    )


@app.callback(
    Input("core-users-refresh-data", "nClicks"),
    prevent_initial_call=True,
)
def handle_refresh_data(nClicks):
    """处理刷新数据逻辑"""

    set_props(
        "global-message",
        {
            "children": fac.AntdMessage(
                type="success",
                content="用户数据刷新成功",
            )
        },
    )

    # 刷新用户列表
    set_props(
        "core-users-table",
        {
            # 重置分页参数
            "pagination": {
                "current": 1,
                "total": len(Users.get_all_users()),  # 获取用户最新总数
                "pageSize": 10,
                "showSizeChanger": False,
            },
        },
    )