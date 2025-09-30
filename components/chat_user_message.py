import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
from feffery_dash_utils.style_utils import style
import dash.html as html


def ChatUserMessage(
    message="如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？",
    message_id=None,
    sender_name="我",
    timestamp="10:31",
    icon="antd-user",
    icon_bg_color="#52c41a",
    message_bg_color="#1890ff",
    message_text_color="white"
):
    """
    用户消息组件
    
    参数:
        message: 消息内容
        message_id: 消息ID
        sender_name: 发送者名称
        timestamp: 时间戳
        icon: 发送者头像图标
        icon_bg_color: 头像背景颜色
        message_bg_color: 消息背景颜色
        message_text_color: 消息文本颜色
    
    返回:
        用户消息组件的渲染结果
    """
    
    return html.Div(
        [
            # 第一行：时间戳、发送者名称和头像（纵向居中对齐）
            fac.AntdRow(
                [
                    fac.AntdCol(
                        [
                            fac.AntdText(timestamp, type="secondary", style=style(fontSize="12px", marginRight="8px")),
                            fac.AntdText(sender_name, strong=True)
                        ],
                        flex="auto",
                        style=style(display="flex", alignItems="center", justifyContent="end")
                    ),
                    fac.AntdCol(
                        fac.AntdAvatar(
                            icon=icon,
                            style=style(backgroundColor=icon_bg_color, width="36px", height="36px")
                        ),
                        flex="none",
                        style=style(marginLeft="12px", display="flex", alignItems="center")
                    )
                ],
                align="middle",
                style=style(padding="0 0 4px 0", minHeight="40px")
            ),
            
            # 第二行：消息内容
            fac.AntdRow(
                [
                    fac.AntdCol(
                        flex="auto"
                    ),
                    fac.AntdCol(
                        fuc.FefferyDiv(
                            fac.AntdText(id=message_id, children=message, style=style(color=message_text_color)),
                            style=style(
                                backgroundColor=message_bg_color,
                                borderRadius="12px 0 12px 12px",
                                padding="12px 16px",
                                maxWidth="80%",
                                width="100%",
                                marginLeft="auto",
                                shadow="hover-shadow-light",
                                scrollbar="simple"
                            )
                        ),
                        flex="auto"
                    )
                ],
                style=style(padding="0 0 8px 0")
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )