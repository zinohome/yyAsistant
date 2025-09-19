import uuid
import time
import dash
from dash import set_props
import feffery_antd_components as fac
from dash.dependencies import Input, Output

from server import app
from models.users import Users


def render():
    """渲染我的信息抽屉"""

    return fac.AntdDrawer(
        id="my-info-drawer",
        title=fac.AntdSpace([fac.AntdIcon(icon="antd-user"), "我的信息"]),
        width="65vw",
        children="我的信息内容区域"
    )


@app.callback(
    Output("my-info-drawer", "children"),
    Input("my-info-drawer", "visible"),
    prevent_initial_call=True,
)
def update_drawer_content(visible):
    """更新抽屉内容"""
    if visible:
        return "我的信息 - 简化版本"
    return dash.no_update


