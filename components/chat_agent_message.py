import dash
from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
import feffery_markdown_components as fmc  # 导入FefferyMarkdown所在的模块
from feffery_dash_utils.style_utils import style
import dash.html as html
from utils.log import log
import time
from dash_iconify import DashIconify  # 新增：导入DashIconify
from components.smart_message_actions import create_smart_message_actions  # 导入智能消息操作栏


def ChatAgentMessage(
    message="您好！我是小妍，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
    message_id=None,
    sender_name="小妍",
    timestamp=None,
    icon=None,
    icon_bg_color="#1890ff",
    message_bg_color="#f5f5f5",
    message_text_color="#000000",
    is_streaming=False,
    original_markdown=None,
):
    """
    AI代理消息组件
    
    参数:
        message: 消息内容
        message_id: 消息ID
        sender_name: 发送者名称
        timestamp: 时间戳
        icon: 发送者头像图标
        icon_bg_color: 头像背景颜色
        message_bg_color: 消息背景颜色
        message_text_color: 消息文本颜色
        is_streaming: 是否为流式响应
        
    返回:
        AI代理消息组件的渲染结果
    """
    
    # 添加调试日志
    #log.debug(f"渲染AI消息组件: ID={message_id}, 内容={message[:20]}..., is_streaming={is_streaming}")
    
    # 确保message_id不为None
    if message_id is None:
        message_id = f"ai-message-{int(time.time())}"
    
    # 如果没有提供timestamp，使用当前时间
    if timestamp is None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    return html.Div(
        className='chat-message ai-message',
        **{"data-streaming": str(is_streaming).lower()},
        children=[
            # 隐藏存储原始Markdown内容
            dcc.Store(
                id={'type': 'ai-chat-x-original-markdown', 'index': message_id},
                data=original_markdown or message
            ),
            # 第一行：头像、发送者名称和时间戳（纵向居中对齐）
            fac.AntdRow(
                [
                    fac.AntdCol(
                        fac.AntdAvatar(
                            mode='image',
                            src="/assets/imgs/girl-avatar.png",
                            alt="小妍头像",
                            size=36,
                            shape="circle",
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
                            children=[
                                fmc.FefferyMarkdown(id=message_id, className="agent-message-markdown-body", markdownStr=message, markdownBaseClassName="theme-pie", style=style(color=message_text_color)),
                                #fac.AntdText(id=message_id, children=message, style=style(color=message_text_color)),
                            ],
                            style=style(
                                backgroundColor=message_bg_color,
                                borderRadius="0 12px 12px 12px",
                                #padding="12px 16px",
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
            
            # 第三行：智能消息操作栏（使用新的智能操作栏）
            create_smart_message_actions(
                message_id=message_id,
                current_state='SUCCESS',  # 默认成功状态
                error_info=None,
                is_streaming=is_streaming
            )
        ],
        style=style(marginBottom="16px", padding="16px 24px 0 24px")
    )

