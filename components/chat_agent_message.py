import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style
from dash.dependencies import Input, Output, State, MATCH
from server import app


def render(
    message="您好！我是智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
    sender_name="智能助手",
    timestamp="10:30",
    icon="antd-robot",
    icon_bg_color="#1890ff"
):
    """
    智能助手消息组件
    
    参数:
        message: 消息内容
        sender_name: 发送者名称
        timestamp: 时间戳
        icon: 发送者头像图标
        icon_bg_color: 头像背景颜色
    
    返回:
        智能助手消息组件的渲染结果
    """
    
    return fac.AntdRow(
        [
            fac.AntdCol(
                fac.AntdAvatar(
                    icon=icon,
                    style=style(backgroundColor=icon_bg_color, width="36px", height="36px")
                ),
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                fac.AntdText(sender_name, strong=True),
                                flex="none",
                                style=style(marginRight="8px")
                            ),
                            fac.AntdCol(
                                fac.AntdText(timestamp, type="secondary", style=style(fontSize="12px")),
                                flex="none"
                            )
                        ],
                        justify="start",
                        style=style(marginBottom="4px")
                    ),
                    # 使用FefferyDiv替换AntdCard
                    fuc.FefferyDiv(
                        fac.AntdText(message),
                        style=style(
                            backgroundColor="#f5f5f5",
                            borderRadius="0 12px 12px 12px",
                            padding="12px 16px",
                            maxWidth="80%",
                            width="100%",
                            # 添加FefferyDiv特有的属性
                            shadow="hover-shadow-light",  # 添加悬浮阴影效果
                            scrollbar="simple"  # 如果消息内容过长，使用简洁的滚动条
                        )
                    ),
                    # 添加底部操作栏
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                fac.AntdSpace(
                                    [
                                        fac.AntdIcon(
                                            icon='antd-reload',
                                            style=style(fontSize=16, color='rgba(0,0,0,0.45)')
                                        ),
                                        fac.AntdIcon(
                                            icon='antd-copy',
                                            style=style(fontSize=16, color='rgba(0,0,0,0.45)')
                                        ),
                                        DashIconify(icon="mingcute:thumb-up-2-line",
                                            width=20,
                                            height=20,
                                            rotate=0,
                                            flip="horizontal",
                                        ),
                                        DashIconify(icon="mingcute:thumb-down-2-line",
                                            width=20,
                                            height=20,
                                            rotate=0,
                                            flip="horizontal",
                                        ),
                                    ],
                                    size=16
                                ),
                                style=style(paddingLeft="4px")
                            )
                        ],
                        justify="start",
                        style=style(marginTop="8px")
                    )
                ],
                flex="auto"
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )

