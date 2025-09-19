import uuid
import time
import dash
from dash import set_props
from flask_login import current_user
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from dash.dependencies import Input, Output, State
from werkzeug.security import generate_password_hash

from server import app
from models.users import Users


def render():
    """渲染我的信息抽屉"""

    return fac.AntdDrawer(
        id="my-info-drawer",
        title=fac.AntdSpace([fac.AntdIcon(icon="antd-user"), "我的信息"]),
        width="65vw",
    )


@app.callback(
    [
        Output("my-info-drawer", "children"),
        Output("my-info-drawer", "loading", allow_duplicate=True),
    ],
    Input("my-info-drawer", "visible"),
    prevent_initial_call=True,
)
def render_my_info_drawer(visible):
    """每次我的信息抽屉打开后，动态更新内容"""

    if visible:
        time.sleep(0.5)

        # 查询当前用户信息
        match_user = Users.get_user(current_user.id)

        return [
            fac.AntdForm(
                [
                    fac.AntdFormItem(
                        fac.AntdInput(
                            id="my-info-user-name",
                            placeholder="请输入用户名",
                            allowClear=True,
                        ),
                        label="用户名",
                    ),
                    fac.AntdFormItem(
                        fac.AntdInput(
                            id="my-info-user-password",
                            placeholder="请输入新的密码",
                            mode="password",
                            allowClear=True,
                        ),
                        label="密码",
                        tooltip="一旦填写并确定更新，则视作新的密码",
                    ),
                    fac.AntdFormItem(
                        fac.AntdSelect(
                            id="my-info-user-icon",
                            placeholder="请选择或输入表情作为头像",
                            options=[
                                {"label": emoji, "value": emoji} for emoji in [
                                    "😇", "🤡", "🥸", "👦", "👧", "👨", "👩", "🧑", "👱", "👨‍🦰", "👩‍🦰", "👨‍🦱", "👩‍🦱", "👨‍🦳", "👩‍🦳", "👨‍🦲", "👩‍🦲", "🧔", "👵", "👴", "🧓", "👲", "👳‍♀️", "👳‍♂️", "🧕", "👮‍♂️", "👮‍♀️", "👷‍♂️", "👷‍♀️", "💂‍♂️", "💂‍♀️", "🕵️‍♂️", "🕵️‍♀️", "👩‍⚕️", "👨‍⚕️", "👩‍🌾", "👨‍🌾", "👩‍🍳", "👨‍🍳", "👩‍🎓", "👨‍🎓", "👩‍🎤", "👨‍🎤", "👩‍🏫", "👨‍🏫", "👩‍🏭", "👨‍🏭", "👩‍💻", "👨‍💻", "👩‍💼", "👨‍💼", "👩‍🔧", "👨‍🔧", "👩‍🔬", "👨‍🔬", "👩‍🎨", "👨‍🎨", "👩‍🚒", "👨‍🚒", "👩‍✈️", "👨‍✈️", "👩‍🚀", "👨‍🚀", "👩‍⚖️", "👨‍⚖️"
                                ]
                            ],
                        ),
                        label="用户头像",
                    ),
                ],
                id="my-info-form",
                key=str(uuid.uuid4()),  # 强制刷新
                enableBatchControl=True,
                layout="vertical",
                values={
                    "my-info-user-name": match_user.user_name,
                    "my-info-user-icon": match_user.user_icon
                },
                style=style(marginTop=32),
            ),
            False,
        ]

    return dash.no_update


@app.callback(
    Input("my-info-drawer", "okCounts"),
    [State("my-info-form", "values")],
    prevent_initial_call=True,
)
def handle_my_info_update(okCounts, values):
    """处理个人信息更新逻辑"""

    # 获取表单数据
    values = values or {}

    # 检查表单数据完整性
    if not values.get("my-info-user-name"):
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
        match_user = Users.get_user_by_name(values["my-info-user-name"])

        # 若与其他用户用户名重复
        if match_user and match_user.user_id != current_user.id:
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
            # 更新用户信息
            update_data = {
                "user_name": values["my-info-user-name"],
                "user_icon": values.get("my-info-user-icon", "")
            }
            
            # 如果填写了密码，则更新密码
            if values.get("my-info-user-password"):
                update_data["password_hash"] = generate_password_hash(
                    values["my-info-user-password"]
                )
            
            Users.update_user(user_id=current_user.id, **update_data)

            set_props(
                "global-message",
                {
                    "children": fac.AntdMessage(
                        type="success",
                        content="用户信息更新成功，页面即将刷新",
                    )
                },
            )
            # 页面延时刷新
            set_props(
                "global-reload",
                {"reload": True, "delay": 2000},
            )