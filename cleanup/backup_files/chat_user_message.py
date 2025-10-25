import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
from feffery_dash_utils.style_utils import style
import dash.html as html
import dash.dcc as dcc


def ChatUserMessage(
    message="如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？",
    message_id=None,
    sender_name="我",
    timestamp="10:31",
    icon="antd-user",
    icon_bg_color="#52c41a",
    message_bg_color="#1890ff",
    message_text_color="white",
    original_content=None
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
        original_content: 原始消息内容（用于复制功能）
    
    返回:
        用户消息组件的渲染结果
    """
    
    return html.Div(
        className='chat-message user-message',
        children=[
            # 隐藏存储原始消息内容
            dcc.Store(
                id={'type': 'user-chat-x-original-content', 'index': message_id},
                data=original_content or message
            ),
            
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
                            fac.AntdText(
                                id=message_id,
                                children=message,
                                style=style(
                                    color=message_text_color,
                                    whiteSpace="pre-wrap"  # 保留换行与空白
                                )
                            ),
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
            ),
            
            # 第三行：底部操作栏（新增）
            fac.AntdRow(
                [
                    fac.AntdCol(
                        flex="auto"
                    ),
                    fac.AntdCol(
                        html.Div(
                            fac.AntdSpace(
                                [
                                    fac.AntdButton(
                                        icon=fac.AntdIcon(icon='antd-reload'),
                                        id={'type': 'user-chat-x-regenerate', 'index': message_id},
                                        type="text",
                                        size="small",
                                        nClicks=0,
                                        style=style(
                                            fontSize=16, 
                                            color='rgba(0,0,0,0.75)',
                                            padding='4px 8px',
                                            minWidth='auto',
                                            height='auto'
                                        )
                                    ),
                                    fac.AntdButton(
                                        icon=fac.AntdIcon(icon='antd-copy'),
                                        id={'type': 'user-chat-x-copy', 'index': message_id},
                                        type="text",
                                        size="small",
                                        nClicks=0,
                                        style=style(
                                            fontSize=16, 
                                            color='rgba(0,0,0,0.75)',
                                            padding='4px 8px',
                                            minWidth='auto',
                                            height='auto'
                                        )
                                    )
                                ],
                                size=16
                            ),
                            className="message-actions"
                        ),
                        style=style(
                            maxWidth="80%",
                            width="100%",
                            marginLeft="auto",
                            display="flex",
                            justifyContent="flex-end"
                        )
                    )
                ],
                style=style(padding="0 0 8px 0")
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )