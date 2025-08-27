import dash
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
import html

# 令对应当前页面的回调函数子模块生效
import callbacks.core_pages_c.chat_c  # noqa: F401


def render():
    """子页面：AntDesign X风格AI聊天界面"""

    return fac.AntdSpace(
        [
            # 面包屑导航
            fac.AntdBreadcrumb(items=[
                {"title": "AI助手"},
                {"title": "智能对话"}
            ]),
            
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
                            # 左侧会话列表
                            fac.AntdCol(
                                [
                                    # 搜索框区域
                                    fac.AntdInput(
                                        id="ai-chat-x-session-search",
                                        placeholder="搜索会话内容",
                                        prefix=fac.AntdIcon(icon="antd-search"),
                                        size="middle",
                                        style=style(
                                            marginBottom="16px",
                                            borderRadius="6px"
                                        )
                                    ),
                                    
                                    # 会话列表区域
                                    fuc.FefferyDiv(
                                        [
                                            fac.AntdSpace(
                                                [
                                                    fac.AntdCard(
                                                        [
                                                            fac.AntdRow(
                                                                [
                                                                    fac.AntdCol(
                                                                        fac.AntdText(
                                                                            item["title"], 
                                                                            strong=True,
                                                                            ellipsis=True
                                                                        ),
                                                                        flex="auto"
                                                                    ),
                                                                    fac.AntdCol(
                                                                        [
                                                                            # 未读消息提示
                                                                            *( [
                                                                                fac.AntdBadge(
                                                                                    count=item["unread"],
                                                                                    showZero=False,
                                                                                    style=style(
                                                                                        backgroundColor="#1890ff",
                                                                                        marginRight="4px"
                                                                                    )
                                                                                )
                                                                            ] if item["unread"] > 0 else [] ),
                                                                            # 时间
                                                                            fac.AntdText(
                                                                                item["time"], 
                                                                                type="secondary",
                                                                                style=style(fontSize="12px")
                                                                            )
                                                                        ],
                                                                        flex="none",
                                                                        style=style(textAlign="right")
                                                                    )
                                                                ],
                                                                style=style(marginBottom="4px")
                                                            ),
                                                            fac.AntdText(
                                                                item["content"], 
                                                                type="secondary",
                                                                ellipsis=True,
                                                                style=style(fontSize="12px")
                                                            )
                                                        ],
                                                        hoverable=True,
                                                        id={"type": "ai-chat-x-session-item", "index": item["key"]},
                                                        style=style(marginBottom="8px", cursor="pointer")
                                                    )
                                                    for item in [
                                                        {"key": "1", "title": "如何使用Dash框架", "time": "10:30", "content": "Dash是一个用于构建分析型Web应用的Python框架...", "unread": 0},
                                                        {"key": "2", "title": "数据可视化最佳实践", "time": "昨天", "content": "数据可视化需要考虑用户体验和数据准确性...", "unread": 2},
                                                        {"key": "3", "title": "Python性能优化技巧", "time": "周一", "content": "使用生成器、避免全局变量、利用内置函数...", "unread": 0}
                                                    ]
                                                ],
                                                id="ai-chat-x-session-list",
                                                direction="vertical",
                                                style=style(width="100%")
                                            )
                                        ],
                                        style=style(height="calc(100% - 52px)", overflow="auto", padding="8px")
                                    )
                                ],
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
                                                # AI欢迎消息
                                                fac.AntdRow(
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
                                                                fac.AntdText("10:30", type="secondary", style=style(fontSize="12px")),
                                                                fac.AntdCard(
                                                                    "您好！我是Ant Design X风格的智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
                                                                    size="small",
                                                                    variant='borderless',
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
                                                ),
                                                # 功能提示卡片
                                                fac.AntdRow(
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
                                                                variant='borderless',
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
                                                ),
                                                # 用户消息示例
                                                fac.AntdRow(
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
                                                                            fac.AntdText("10:31", type="secondary", style=style(fontSize="12px")),
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
                                                                    "如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？",
                                                                    size="small",
                                                                    variant='borderless',
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
                                                                style=style(backgroundColor="#52c41a", width="36px", height="36px")
                                                            ),
                                                            flex="none"
                                                        )
                                                    ],
                                                    style=style(marginBottom="16px", padding="0 24px")
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
                style=style(
                    width="100%",
                    borderRadius="8px",
                    overflow="hidden"
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