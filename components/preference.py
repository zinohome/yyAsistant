import dash
from dash import set_props
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State
from dash.dependencies import ClientsideFunction
from server import app


def render():
    """渲染偏好设置抽屉"""

    return fac.AntdDrawer(
        id="preference-drawer",
        title=fac.AntdSpace([fac.AntdIcon(icon="antd-setting"), "偏好设置"]),
        # 移除固定宽度，由回调函数动态设置
        closable=False,  # 隐藏关闭按钮
        maskClosable=False,  # 禁用点击遮罩层关闭
        children="偏好设置内容区域"
    )


@app.callback(
    Output("preference-drawer", "children"),
    Input("preference-drawer", "visible"),
    prevent_initial_call=True,
)
def update_drawer_content(visible):
    """更新抽屉内容"""
    if visible:
        # 使用 Tabs 组织的偏好设置内容
        return [
            fac.AntdTabs(
                items=[
                    {
                        "key": "theme",
                        "label": "主题设置",
                        "children": fac.AntdSpace(
                    [
                                fac.AntdText("选择主题："),
                        fac.AntdRadioGroup(
                            options=[
                                {
                                    'label': "浅色主题",
                                    'value': "light"
                                },
                                {
                                    'label': "深色主题", 
                                    'value': "dark"
                                },
                                {
                                    'label': "跟随系统",
                                    'value': "system"
                                }
                            ],
                            defaultValue="light",
                            id="theme-radio-group"
                        )
                    ],
                    direction="vertical",
                            style={"width": "100%", "padding": "16px 0"}
                        )
                    },
                    {
                        "key": "language",
                        "label": "语言设置",
                        "children": fac.AntdSpace(
                    [
                                fac.AntdText("选择语言："),
                        fac.AntdSelect(
                            options=[
                                {"label": "简体中文", "value": "zh-CN"},
                                {"label": "English", "value": "en-US"}
                            ],
                            defaultValue="zh-CN",
                                    id="language-select",
                            style={"width": 150}
                        )
                    ],
                    direction="vertical",
                            style={"width": "100%", "padding": "16px 0"}
                        )
                    }
                ],
                defaultActiveKey="theme",
                style={"marginBottom": 16}
                ),
                fac.AntdDivider(),
            fac.AntdSpace(
                [
                fac.AntdButton(
                        "保存",
                    type="primary",
                        id="preference-save-btn",
                    style={"marginRight": 8}
                ),
                    fac.AntdButton(
                        "取消",
                        id="preference-cancel-btn"
                    )
            ],
                style={"width": "100%", "justifyContent": "flex-end", "padding": "8px 0"}
        )
        ]
    return dash.no_update


@app.callback(
    Output("preference-drawer", "visible"),
    Input("preference-save-btn", "nClicks"),
    Input("preference-cancel-btn", "nClicks"),
    prevent_initial_call=True,
)
def close_drawer_on_button_click(save_clicks, cancel_clicks):
    """点击保存或取消按钮时关闭抽屉"""
    # 当任一按钮被点击时（nClicks 不为 None），关闭抽屉
    if save_clicks is not None or cancel_clicks is not None:
        return False
    return dash.no_update


# 在文件末尾添加以下代码
app.clientside_callback(
    ClientsideFunction(
        namespace="clientside_basic",
        function_name="handleResponsiveDrawerWidth"
    ),
    Output("preference-drawer", "width"),
    Input("preference-drawer", "visible"),
    prevent_initial_call=False
)