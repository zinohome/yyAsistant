from dash import html, dcc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


def render():
    """子页面：首页渲染简单示例"""

    return fac.AntdSpace(
        [
            fac.AntdBreadcrumb(items=[{"title": "首页"}, {"title": "快速导航"}]),
            fac.AntdAlert(
                type="info",
                showIcon=True,
                message="快速导航",
                description=fac.AntdSpace(
                        [
                            fac.AntdText("点击下方按钮跳转到聊天页面："),
                            fac.AntdButton(
                                "前往聊天",
                                type="primary",
                                icon=fac.AntdIcon(icon="antd-message"),
                                href="/core/chat",
                                target="_self",
                                style={"marginTop": "8px"}
                            )
                        ],
                        direction="vertical",
                        style=style(width="100%")
                    ),
            ), 
        ],
        direction="vertical",
        style=style(width="100%"),
    )
