import dash
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
import html

# 导入聊天组件
from components.chat_welcome_message import render as render_welcome_message
from components.chat_feature_hints import render as render_feature_hints
from components.chat_user_message import render as render_user_message
from components.chat_session_list import render as render_session_list

# 令对应当前页面的回调函数子模块生效
import callbacks.core_pages_c.chat_c  # noqa: F401


def render():
    """子页面：AntDesign X风格AI聊天界面"""

    return fac.AntdSpace(
        [            
            # 页面标题和操作按钮区域
            fac.AntdRow(
                [
                    fac.AntdCol(
                        flex='auto',
                        children=fac.AntdPageHeader(
                            title="智能对话助手",
                            subTitle="与AI进行自然语言交互，获取智能助手的帮助",
                            showBackIcon=False  # 可选：隐藏返回按钮
                        )
                    ),
                    fac.AntdCol(
                        children=fac.AntdSpace(
                            [
                                fac.AntdButton(
                                    "历史会话",
                                    id="ai-chat-x-history-btn",
                                    type="text"
                                ),
                                fac.AntdButton(
                                    "新建会话",
                                    id="ai-chat-x-new-conversation",
                                    type="primary",
                                    icon=fac.AntdIcon(icon="antd-plus")
                                )
                            ]
                        )
                    )
                ],
                gutter=16,
                align='middle'
            ),
            
            # 聊天界面主容器 - 使用卡片组件包装
            fac.AntdCard(
                [
                    # 聊天主体区域（左右布局）
                    fac.AntdRow(
                        [
                            # 左侧会话列表 - 使用组件
                            fac.AntdCol(
                                render_session_list(),
                                flex="none",
                                style=style(width="280px", padding="16px", borderRight="1px solid #f0f0f0")
                            ),
                            
                            # 右侧聊天内容区域
                            fac.AntdCol(
                                fuc.FefferyDiv(
                                    [
                                        # 聊天头部信息
                                        fac.AntdRow(
                                            [
                                                fac.AntdCol(
                                                    [
                                                        fac.AntdText("当前会话", strong=True),
                                                        fac.AntdDivider(direction="vertical", style=style(margin="0 12px")),
                                                        fac.AntdTag(
                                                            "进行中",
                                                            color="blue",
                                                            icon=fac.AntdIcon(icon="antd-check-circle", style=style(fontSize="12px"))
                                                        )
                                                    ],
                                                    flex="auto"
                                                ),
                                                fac.AntdCol(
                                                    fac.AntdSpace(
                                                        [
                                                            fac.AntdButton(
                                                                icon=fac.AntdIcon(icon="antd-star"),
                                                                id="ai-chat-x-favorite-btn",
                                                                type="text"
                                                            ),
                                                            fac.AntdButton(
                                                                icon=fac.AntdIcon(icon="antd-more"),
                                                                id="ai-chat-x-more-btn",
                                                                type="text"
                                                            )
                                                        ],
                                                        size="small"
                                                    ),
                                                    flex="none"
                                                )
                                            ],
                                            style=style(padding="12px 24px", borderBottom="1px solid #f0f0f0", backgroundColor="#fff")
                                        ),
                                        
                                        # 聊天历史区域
                                        fuc.FefferyDiv(
                                            id="ai-chat-x-history",
                                            children=[
                                                # 使用欢迎消息组件
                                                render_welcome_message(),
                                                
                                                # 使用功能提示卡片组件
                                                render_feature_hints(),
                                                
                                                # 使用用户消息组件
                                                render_user_message(
                                                    message="如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？"
                                                )
                                            ],
                                            style=style(
                                                height="calc(100% - 170px)",
                                                overflowY="auto",
                                                backgroundColor="#fafafa"
                                            )
                                        ),
                                        
                                        # 输入区域
                                        fuc.FefferyDiv(
                                            [
                                                # 工具栏
                                                fac.AntdSpace(
                                                    [
                                                        fac.AntdButton(
                                                            icon=fac.AntdIcon(icon="antd-plus-circle"),
                                                            type="text",
                                                            title="上传文件"
                                                        ),
                                                        fac.AntdButton(
                                                            icon=fac.AntdIcon(icon="antd-picture"),
                                                            type="text",
                                                            title="上传图片"
                                                        ),
                                                        fac.AntdDivider(direction="vertical", style=style(margin="0 8px")),
                                                        fac.AntdButton(
                                                            icon=fac.AntdIcon(icon="antd-smile"),
                                                            type="text",
                                                            title="表情"
                                                        ),
                                                        fac.AntdButton(
                                                            icon=fac.AntdIcon(icon="antd-save"),
                                                            type="text",
                                                            title="保存对话"
                                                        )
                                                    ],
                                                    style=style(padding="8px 0")
                                                ),
                                                
                                                # 输入框和发送按钮
                                                fac.AntdRow(
                                                    [
                                                        fac.AntdCol(
                                                            flex="auto",
                                                            children=fac.AntdInput(
                                                                id="ai-chat-x-input",
                                                                placeholder="输入您的问题...",
                                                                autoSize={"minRows": 3, "maxRows": 6},
                                                                showCount=True,
                                                                maxLength=2000,
                                                                style=style(
                                                                    borderRadius="8px 0 0 8px",
                                                                    borderRight="none"
                                                                )
                                                            )
                                                        ),
                                                        fac.AntdCol(
                                                            flex="none",
                                                            children=fac.AntdButton(
                                                                "发送",
                                                                id="ai-chat-x-send-btn",
                                                                type="primary",
                                                                icon=fac.AntdIcon(icon="antd-right"),
                                                                style=style(
                                                                    height="100%",
                                                                    borderRadius="0 8px 8px 0",
                                                                    padding="0 24px"
                                                                )
                                                            )
                                                        )
                                                    ],
                                                    gutter=0
                                                ),
                                                
                                                # 底部提示
                                                fac.AntdRow(
                                                    [
                                                        fac.AntdCol(
                                                            [
                                                                fac.AntdText(
                                                                    "按 Enter 发送，Shift + Enter 换行",
                                                                    type="secondary",
                                                                    style=style(fontSize="12px")
                                                                )
                                                            ],
                                                            flex="auto",
                                                            style=style(textAlign="left", paddingTop="8px")
                                                        ),
                                                        fac.AntdCol(
                                                            [
                                                                fac.AntdButton(
                                                                    "清空对话",
                                                                    id="ai-chat-x-clear-btn",
                                                                    type="text",
                                                                    style=style(fontSize="12px")
                                                                )
                                                            ],
                                                            flex="none"
                                                        )
                                                    ]
                                                )
                                            ],
                                            style=style(
                                                padding="16px 24px",
                                                backgroundColor="#fff",
                                                borderTop="1px solid #f0f0f0"
                                            )
                                        )
                                    ],
                                    style=style(
                                        height="calc(100vh - 210px)",
                                        display="flex",
                                        flexDirection="column"
                                    )
                                ),
                                flex="auto",
                                style=style(padding="0")
                            )
                        ],
                        gutter=0,
                        style=style(width="100%")
                    )
                ],
                variant='borderless',
                styles={'header': {'display': 'none'}},
                style=style(
                    width="100%",
                    borderRadius="8px",
                    overflow="hidden",
                )
            )
        ],
        direction="vertical",
        style=style(
            width="100%",
            height="100vh",
            padding="16px",
            margin="0",
            backgroundColor="#fff",
            boxSizing="border-box",
            display="flex",
            flexDirection="column"
        )
    )