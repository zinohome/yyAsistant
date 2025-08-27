import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


def render(
    message="您好！我是智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
    sender_name="智能助手",
    timestamp="10:30",
    icon="antd-robot",
    icon_bg_color="#1890ff"
):
    """
    聊天欢迎消息组件
    
    参数:
        message: 欢迎消息内容
        sender_name: 发送者名称
        timestamp: 时间戳
        icon: 发送者头像图标
        icon_bg_color: 头像背景颜色
    
    返回:
        欢迎消息组件的渲染结果
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
                    fac.AntdText(sender_name, strong=True, style=style(marginRight="8px")),
                    fac.AntdText(timestamp, type="secondary", style=style(fontSize="12px")),
                    fac.AntdCard(
                        message,
                        size="small",
                        variant='borderless',
                        styles={'header': {'display': 'none'}},
                        style=style(
                            backgroundColor="#f5f5f5",
                            borderRadius="12px 12px 12px 0",
                            padding="12px 16px",
                            maxWidth="70%",
                            marginTop="4px"
                        )
                    )
                ],
                flex="auto",
                style=style(textAlign="left")
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )