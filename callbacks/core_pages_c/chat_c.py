import dash
from dash import Input, Output, State, ctx
import feffery_antd_components as fac
from server import app
from feffery_dash_utils.style_utils import style
import html
import time
from datetime import datetime


@app.callback(
    Output("ai-chat-x-history", "children"),
    Output("ai-chat-x-input", "value"),
    Input("ai-chat-x-send-button", "nClicks"),
    State("ai-chat-x-input", "value"),
    State("ai-chat-x-history", "children"),
    prevent_initial_call=True
)
def handle_send_message(nClicks, message, chat_history):
    """处理发送消息逻辑"""
    
    # 如果消息为空，不处理
    if not message or not message.strip():
        return dash.no_update, dash.no_update
    
    # 获取当前时间
    current_time = datetime.now().strftime("%H:%M")
    
    # 创建用户消息组件
    user_message = fac.AntdRow(
        [
            fac.AntdCol(
                flex="auto",
                style=style(textAlign="right")
            ),
            fac.AntdCol(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                fac.AntdText(current_time, type="secondary", style=style(fontSize="12px")),
                                flex="none",
                                style=style(marginRight="8px")
                            ),
                            fac.AntdCol(
                                fac.AntdText("我", strong=True),
                                flex="none"
                            )
                        ],
                        justify="end",
                        style=style(marginBottom="4px")
                    ),
                    fac.AntdCard(
                        html.P(message.strip()),
                        size="small",
                        bordered=False,
                        style=style(
                            backgroundColor="#1890ff",
                            color="white",
                            borderRadius="12px 12px 0 12px",
                            padding="12px 16px",
                            maxWidth="70%"
                        )
                    )
                ],
                flex="auto",
                style=style(textAlign="right", paddingRight="12px")
            ),
            fac.AntdCol(
                fac.AntdAvatar(
                    icon="antd-user",
                    style=style(backgroundColor="#87d068", width="36px", height="36px")
                ),
                flex="none",
                style=style(marginLeft="12px")
            )
        ],
        style=style(marginBottom="16px", padding="0 24px")
    )
    
    # 创建AI回复消息组件（AntDesign X风格的详细回复）
    ai_reply = "感谢您的提问！这是一个示例回复。在实际应用中，这里会显示AI生成的回答内容。"
    if "antdesign" in message.lower() or "ant design" in message.lower():
        ai_reply = "Ant Design X风格的设计要点包括：\n1. 简洁专业的视觉语言\n2. 统一的组件体系\n3. 合理的信息层级\n4. 良好的交互反馈\n5. 响应式设计支持\n6. 深色模式适配"
    elif "代码" in message or "code" in message.lower():
        ai_reply = "您想了解代码相关的内容吗？我可以帮助您：\n- 解释代码逻辑\n- 提供代码优化建议\n- 解决编程问题\n- 生成示例代码\n请告诉我您具体需要哪方面的帮助。"
    
    ai_message = fac.AntdRow(
        [
            fac.AntdCol(
                fac.AntdAvatar(
                    icon="antd-robot",
                    style=style(backgroundColor="#1890ff", width="36px", height="36px")
                ),
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                [
                    fac.AntdText("智能助手", strong=True, style=style(marginRight="8px")),
                    fac.AntdText(current_time, type="secondary", style=style(fontSize="12px")),
                    fac.AntdCard(
                        [
                            # 为回复添加标签，提升专业感
                            fac.AntdSpace(
                                [
                                    fac.AntdTag("专业建议", color="blue", bordered=False, style=style(marginBottom="8px"))
                                ]
                            ),
                            # 回复内容
                            html.P(ai_reply.replace('\n', '<br/>')),
                            # 添加操作按钮，提升交互性
                            fac.AntdSpace(
                                [
                                    fac.AntdButton(
                                        "👍 有用",
                                        id={"type": "ai-chat-x-feedback", "index": "useful"},
                                        type="text",
                                        size="small"
                                    ),
                                    fac.AntdButton(
                                        "👎 没用",
                                        id={"type": "ai-chat-x-feedback", "index": "useless"},
                                        type="text",
                                        size="small"
                                    ),
                                    fac.AntdButton(
                                        "📋 复制",
                                        id={"type": "ai-chat-x-copy", "index": str(int(time.time()))},
                                        type="text",
                                        size="small"
                                    )
                                ],
                                style=style(marginTop="8px")
                            )
                        ],
                        size="small",
                        bordered=False,
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
        style=style(marginBottom="16px", padding="0 24px")
    )
    
    # 更新聊天历史
    if chat_history:
        chat_history.append(user_message)
        chat_history.append(ai_message)
    else:
        chat_history = [user_message, ai_message]
    
    # 清空输入框
    return chat_history, ""


@app.callback(
    Output("ai-chat-x-history", "children", allow_duplicate=True),
    Input("ai-chat-x-new-conversation", "nClicks"),
    prevent_initial_call=True
)
def handle_new_conversation(nClicks):
    """处理新建会话逻辑"""
    
    # 获取当前时间
    current_time = datetime.now().strftime("%H:%M")
    
    # 创建欢迎消息
    welcome_message = fac.AntdRow(
        [
            fac.AntdCol(
                fac.AntdAvatar(
                    icon="antd-robot",
                    style=style(backgroundColor="#1890ff", width="36px", height="36px")
                ),
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                [
                    fac.AntdText("智能助手", strong=True, style=style(marginRight="8px")),
                    fac.AntdText(current_time, type="secondary", style=style(fontSize="12px")),
                    fac.AntdCard(
                        html.P("您好！我是Ant Design X风格的智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。"),
                        size="small",
                        bordered=False,
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
    
    # 添加功能提示卡片
    feature_card = fac.AntdRow(
        [
            fac.AntdCol(
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                fac.AntdCard(
                    [
                        fac.AntdText("💡 您可以：", type="secondary"),
                        fac.AntdSpace(
                            [
                                fac.AntdTag("询问技术问题", color="blue", bordered=False),
                                fac.AntdTag("获取设计建议", color="purple", bordered=False),
                                fac.AntdTag("寻求代码帮助", color="green", bordered=False)
                            ],
                            direction="vertical",
                            style=style(width="100%")
                        )
                    ],
                    size="small",
                    bordered=True,
                    type="inner",
                    style=style(
                        borderRadius="8px",
                        padding="12px",
                        maxWidth="70%",
                        backgroundColor="#f0f8ff"
                    )
                ),
                flex="auto",
                style=style(textAlign="left")
            )
        ],
        style=style(marginBottom="16px", padding="0 24px")
    )
    
    return [welcome_message, feature_card]


@app.callback(
    Output("ai-chat-x-session-list", "dataSource"),
    Input("ai-chat-x-new-conversation", "nClicks"),
    Input("ai-chat-x-send-button", "nClicks"),
    State("ai-chat-x-session-list", "dataSource"),
    State("ai-chat-x-input", "value"),
    prevent_initial_call=True
)
def update_session_list(new_conversation_clicks, send_message_clicks, sessions, message):
    """更新会话列表"""
    
    # 获取当前时间/日期
    now = datetime.now()
    if now.hour < 12:
        time_display = "上午"
    else:
        time_display = "下午"
    time_display += now.strftime("%H:%M")
    
    if ctx.triggered_id == "ai-chat-x-new-conversation":
        # 新建会话
        new_session = {
            "key": str(len(sessions) + 1),
            "title": "新会话",
            "time": time_display,
            "content": "开始了一个新的会话",
            "unread": 0
        }
        # 将新会话添加到列表顶部
        return [new_session] + sessions
    elif ctx.triggered_id == "ai-chat-x-send-button" and message:
        # 更新最近的会话
        if sessions:
            # 提取消息的前30个字符作为会话内容摘要
            content_preview = message.strip()[:30] + ("..." if len(message.strip()) > 30 else "")
            # 如果是第一条消息，可以设置会话标题
            if len(sessions) > 0 and sessions[0]["title"] == "新会话":
                # 使用消息的前20个字符作为标题
                title = message.strip()[:20] + ("..." if len(message.strip()) > 20 else "")
                sessions[0]["title"] = title
            # 更新会话内容和时间
            sessions[0]["content"] = content_preview
            sessions[0]["time"] = time_display
        return sessions
    
    return dash.no_update


@app.callback(
    Output("ai-chat-x-history", "children", allow_duplicate=True),
    Input({"type": "ai-chat-x-session-item", "index": dash.ALL}, "nClicks"),
    prevent_initial_call=True
)
def switch_conversation(_):
    """切换会话"""
    # 获取会话ID
    session_id = ctx.triggered_id["index"]
    
    # 获取当前时间
    current_time = datetime.now().strftime("%H:%M")
    
    # 创建切换会话的提示消息
    switch_message = fac.AntdRow(
        [
            fac.AntdCol(
                fac.AntdAvatar(
                    icon="antd-robot",
                    style=style(backgroundColor="#1890ff", width="36px", height="36px")
                ),
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                [
                    fac.AntdText("智能助手", strong=True, style=style(marginRight="8px")),
                    fac.AntdText(current_time, type="secondary", style=style(fontSize="12px")),
                    fac.AntdCard(
                        [
                            # 添加切换会话的标签
                            fac.AntdSpace(
                                [
                                    fac.AntdTag("会话切换", color="purple", bordered=False, style=style(marginBottom="8px"))
                                ]
                            ),
                            html.P(f"已切换到会话 #{session_id}。在实际应用中，这里会显示该会话的历史记录。")
                        ],
                        size="small",
                        bordered=False,
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
    
    return [switch_message]


@app.callback(
    Output("ai-chat-x-session-search", "value"),
    Input("ai-chat-x-session-search", "keyPressEnter"),
    State("ai-chat-x-session-search", "value"),
    prevent_initial_call=True
)
def handle_search_session(keyPressEnter, search_value):
    """处理会话搜索"""
    # 这里可以实现会话搜索逻辑
    # 目前简单返回搜索值
    return search_value