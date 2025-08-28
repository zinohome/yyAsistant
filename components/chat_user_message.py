import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
from feffery_dash_utils.style_utils import style


def render(
    message="如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？",
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
        sender_name: 发送者名称
        timestamp: 时间戳
        icon: 发送者头像图标
        icon_bg_color: 头像背景颜色
        message_bg_color: 消息背景颜色
        message_text_color: 消息文本颜色
    
    返回:
        用户消息组件的渲染结果
    """
    
    return fac.AntdRow(
        [
            fac.AntdCol(
                flex="auto"
            ),
            fac.AntdCol(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                fac.AntdText(timestamp, type="secondary", style=style(fontSize="12px")),
                                flex="none",
                                style=style(marginRight="8px")
                            ),
                            fac.AntdCol(
                                fac.AntdText(sender_name, strong=True),
                                flex="none"
                            )
                        ],
                        justify="end",
                        style=style(marginBottom="4px")
                    ),
                    # 使用FefferyDiv替换AntdCard
                    fuc.FefferyDiv(
                        fac.AntdText(message, style=style(color=message_text_color)),
                        style=style(
                            backgroundColor=message_bg_color,
                            borderRadius="12px 0 12px 12px",
                            padding="12px 16px",
                            maxWidth="80%",
                            width="100%",
                            marginLeft="auto",
                            # 可以添加FefferyDiv特有的属性
                            shadow="hover-shadow-light",  # 添加悬浮阴影效果
                            scrollbar="simple"  # 如果消息内容过长，使用简洁的滚动条
                        )
                    )
                ],
                flex="auto"
            ),
            fac.AntdCol(
                fac.AntdAvatar(
                    icon=icon,
                    style=style(backgroundColor=icon_bg_color, width="36px", height="36px")
                ),
                flex="none",
                style=style(marginLeft="12px")
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )