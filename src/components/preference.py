import dash
from dash import set_props
import feffery_antd_components as fac
from dash.dependencies import Input, Output
from dash.dependencies import ClientsideFunction
from server import app


def render():
    """渲染偏好设置抽屉"""

    return fac.AntdDrawer(
        id="preference-drawer",
        title=fac.AntdSpace([fac.AntdIcon(icon="antd-setting"), "偏好设置"]),
        # 移除固定宽度，由回调函数动态设置
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
        # 简化版偏好设置内容
        return fac.AntdCard(
            [
                fac.AntdTitle("偏好设置", level=4),
                fac.AntdDivider(),
                fac.AntdSpace(
                    [
                        fac.AntdText("主题设置："),
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
                    style={"width": "100%"}
                ),
                fac.AntdDivider(),
                fac.AntdSpace(
                    [
                        fac.AntdText("语言设置："),
                        fac.AntdSelect(
                            options=[
                                {"label": "简体中文", "value": "zh-CN"},
                                {"label": "English", "value": "en-US"}
                            ],
                            defaultValue="zh-CN",
                            style={"width": 150}
                        )
                    ],
                    direction="vertical",
                    style={"width": "100%"}
                ),
                fac.AntdDivider(),
                fac.AntdButton(
                    "保存设置",
                    type="primary",
                    style={"marginRight": 8}
                ),
                fac.AntdButton("取消")
            ],
            style={"marginBottom": 0}
        )
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