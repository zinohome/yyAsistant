from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style


def ChatFeatureHints(
    message="您好！我是智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
    sender_name="智能助手",
    timestamp="10:30",
    #icon="antd-robot",
    icon=None,
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
    
    return html.Div(
        [
            # 第一行：头像、发送者名称和时间戳（纵向居中对齐）
            fac.AntdRow(
                [
                    fac.AntdCol(
                        fac.AntdAvatar(
                            mode='image',
                            src="/assets/imgs/girl-avatar.png",
                            size=36,
                            shape="circle",
                            alt="智能助手头像",
                            # 🔧 关键修复：完全不传递icon参数，根据Ant Design文档，优先级是 icon > children > src
                            # 如果传递了icon参数（即使是None），都会优先使用icon，导致src无法生效
                            style=style(width="36px", height="36px")
                        ),
                        flex="none",
                        style=style(marginRight="12px", display="flex", alignItems="center")
                    ),
                    fac.AntdCol(
                        [
                            fac.AntdText(sender_name, strong=True),
                            fac.AntdText(
                                timestamp,
                                type="secondary",
                                style=style(fontSize="12px", marginLeft="8px")
                            )
                        ],
                        flex="auto",
                        style=style(display="flex", alignItems="center")
                    )
                ],
                align="middle",
                style=style(padding="0 0 4px 0", minHeight="40px")
            ),
            
            # 第二行：消息内容，保持缩进
            fac.AntdRow(
                [
                    fac.AntdCol(
                        style=style(width="48px", height="0")  # 用于与头像对齐的占位符
                    ),
                    fac.AntdCol(
                        fuc.FefferyDiv(
                            fac.AntdText(message),
                            style=style(
                                backgroundColor="#f5f5f5",
                                borderRadius="0 12px 12px 12px",
                                padding="12px 16px",
                                maxWidth="80%",
                                width="100%",
                                shadow="hover-shadow-light",
                                scrollbar="simple"
                            )
                        ),
                        flex="auto"
                    )
                ],
                style=style(padding="0 0 8px 0")
            ),
            
            # 第三行：底部操作栏
            fac.AntdRow(
                [
                    fac.AntdCol(
                        style=style(width="48px", height="0")  # 用于与头像对齐的占位符
                    ),
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
                justify="start"
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )

