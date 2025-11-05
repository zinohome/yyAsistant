import feffery_utils_components as fuc
import feffery_antd_components as fac
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style
from configs.topics_loader import get_category_topics, get_settings
from configs import BaseConfig


def render(
    placeholder="输入您的问题...",
    max_length=2000,
    topics=None,
    icons=None,
    enable_file_upload=False,
    enable_voice_input=True,
    enable_send_button=True
):
    """
    聊天输入区域组件 - 支持话题提示、附件上传、语音输入等功能
    
    参数:
        placeholder: 输入框占位文本
        max_length: 最大输入长度
        topics: 话题提示列表，如果为None则从配置文件加载
        icons: 话题图标列表，与topics一一对应，如果为None则从配置文件加载
        enable_file_upload: 是否启用文件上传
        enable_voice_input: 是否启用语音输入
        enable_send_button: 是否启用发送按钮
    """
    
    # 如果未提供topics和icons，从配置文件动态加载分类话题
    if topics is None:
        category_topics = get_category_topics()
        topics = [topic['title'] for topic in category_topics]
    if icons is None:
        category_topics = get_category_topics()
        icons = [topic['icon'] for topic in category_topics]
    
    # 获取设置信息
    settings = get_settings()
    max_topics_display = settings.get('max_topics_display', 4)
    
    # 限制显示的话题数量（现在固定显示4个分类）
    if len(topics) > max_topics_display:
        topics = topics[:max_topics_display]
        icons = icons[:max_topics_display]
    
    # 根据配置决定渲染话题提示栏还是工具栏
    bar_mode = BaseConfig.chat_input_bar_mode
    
    # 渲染工具栏
    if bar_mode == "tools":
        toolbar_content = fuc.FefferyDiv(
            [
                fac.AntdSpace(
                    [
                        # 健康档案按钮
                        fuc.FefferyDiv(
                            [
                                fac.AntdIcon(
                                    icon="antd-user",
                                    style=style(marginRight="8px", color="#666")
                                ),
                                "健康档案"
                            ],
                            id="toolbar-health-record-btn",
                            shadow="hover-shadow-light",
                            style=style(
                                display="flex",
                                alignItems="center",
                                padding="8px 16px",
                                backgroundColor="#f5f5f5",
                                color="#333",
                                borderRadius="6px",
                                cursor="pointer",
                                border="1px solid #e8e8e8",
                                transition="all 0.2s ease",
                                whiteSpace="nowrap"
                            ),
                            enableEvents=['click', 'hover'],
                            nClicks=0
                        ),
                        # 偏好设置按钮
                        fuc.FefferyDiv(
                            [
                                fac.AntdIcon(
                                    icon="antd-setting",
                                    style=style(marginRight="8px", color="#666")
                                ),
                                "偏好设置"
                            ],
                            id="toolbar-preference-btn",
                            shadow="hover-shadow-light",
                            style=style(
                                display="flex",
                                alignItems="center",
                                padding="8px 16px",
                                backgroundColor="#f5f5f5",
                                color="#333",
                                borderRadius="6px",
                                cursor="pointer",
                                border="1px solid #e8e8e8",
                                transition="all 0.2s ease",
                                whiteSpace="nowrap"
                            ),
                            enableEvents=['click', 'hover'],
                            nClicks=0
                        ),
                        # 康泰友聚按钮（暂时禁用）
                        fuc.FefferyDiv(
                            [
                                DashIconify(
                                    icon="material-symbols:groups",
                                    width=16,
                                    height=16,
                                    style=style(marginRight="8px", color="#999")
                                ),
                                "康泰友聚"
                            ],
                            id="toolbar-social-btn",
                            shadow="hover-shadow-light",
                            style=style(
                                display="flex",
                                alignItems="center",
                                padding="8px 16px",
                                backgroundColor="#f5f5f5",
                                color="#999",
                                borderRadius="6px",
                                cursor="not-allowed",
                                border="1px solid #e8e8e8",
                                transition="all 0.2s ease",
                                whiteSpace="nowrap",
                                opacity=0.6
                            ),
                            enableEvents=[],  # 禁用事件
                            nClicks=0
                        )
                    ],
                    wrap=False,
                    style=style(width="100%")
                )
            ],
            scrollbar='hidden',
            style=style(
                display="flex", 
                overflowX="auto",
                marginBottom="8px",
                paddingBottom="4px" 
            )
        )
    else:
        # 渲染话题提示栏（原有逻辑）
        toolbar_content = fuc.FefferyDiv(
            [
                fac.AntdSpace(
                    [
                        fuc.FefferyDiv(
                            [
                                DashIconify(
                                    icon=icons[index],  # 使用icons列表中的图标
                                    width=16,
                                    height=16,
                                    style=style(marginRight="8px", color="#666")
                                ),
                                topic
                            ],
                            id={'type': 'chat-topic', 'index': index},
                            shadow="hover-shadow-light",
                            style=style(
                                display="flex",
                                alignItems="center",
                                padding="8px 16px",  # 更宽的按钮
                                backgroundColor="#f5f5f5",  # 浅灰色背景
                                color="#333",  # 深灰色文字
                                borderRadius="6px",  # 稍大的圆角
                                cursor="pointer",  # 鼠标移到上面显示手型
                                border="1px solid #e8e8e8",  # 更浅的边框
                                transition="all 0.2s ease",  # 平滑过渡
                                whiteSpace="nowrap"  # 关键修改：防止工具项内文本换行
                            ),
                            enableEvents=['click', 'hover'],
                            # 点击事件，暂时置空
                            nClicks=0

                        ) for index, topic in enumerate(topics)
                    ],
                    wrap=False,
                    style=style(width="100%")
                )
            ],
            scrollbar='hidden',
            style=style(
                display="flex", 
                overflowX="auto",
                marginBottom="8px",
                paddingBottom="4px" 
                )
        )
    
    # 统一外框的输入区域容器
    children =  fuc.FefferyDiv(
        [
            # 话题提示栏或工具栏（根据配置决定）
            toolbar_content,
            
            # 输入框区域 - 包含统一外框，支持响应式布局
            fuc.FefferyDiv(
                [
                    # 第一行：附件按钮 + 输入框 + 发送按钮（大屏幕时包含录音和通话按钮）
                    fac.AntdRow(
                        [
                            # 左侧附件上传按钮
                            *( [
                                fac.AntdCol(
                                    flex="none",
                                    children=fac.AntdButton(
                                        icon=DashIconify(icon="entypo:attachment",
                                            width=20,
                                            height=20,
                                            rotate=1,
                                            flip="horizontal",
                                        ),
                                        type="text",
                                        title="上传附件",
                                        style=style(padding="4px 8px")
                                    )
                                )
                            ] if enable_file_upload else [] ),
                            
                            # 输入框
                            fac.AntdCol(
                                flex="auto",
                                children=fac.AntdInput(
                                    id="ai-chat-x-input",
                                    mode="text-area",
                                    placeholder=placeholder,
                                    autoSize={"minRows": 1, "maxRows": 6},
                                    showCount=False,
                                    maxLength=max_length,
                                    variant='borderless',
                                    styles={
                                        'textarea': {
                                            'transition': 'none',
                                            'animation': 'none',
                                            'resize': 'none',
                                            'fontSize': '14px'  # 🔧 统一字体大小为14px
                                        }
                                    },
                                    style=style(
                                        border=None,  # 移除输入框自身的边框
                                        display="flex",
                                        alignItems="center",
                                        minHeight="48px"
                                    )
                                )
                            ),
                            
                            # 右侧按钮组（大屏幕时显示所有按钮，小屏幕时只显示发送按钮）
                            fac.AntdCol(
                                flex="none",
                                children=fac.AntdSpace(
                                    [   
                                        # 发送按钮（上箭头） - 统一样式，所有屏幕都显示
                                        *( [
                                            fac.AntdButton(
                                                icon=fac.AntdIcon(icon="antd-arrow-up"),
                                                id="ai-chat-x-send-btn",
                                                type="primary",
                                                size="large",
                                                style=style(
                                                    padding="8px",
                                                    width="40px",
                                                    height="40px",
                                                    borderRadius="8px",
                                                    backgroundColor="#1890ff",
                                                    borderColor="#1890ff",
                                                    boxShadow="0 2px 4px rgba(24, 144, 255, 0.2)"
                                                )
                                            )
                                        ] if enable_send_button else [] ),

                                        # 录音按钮 - 统一样式，大屏幕（≥576px）时显示在第一行
                                        *( [
                                            fac.AntdButton(
                                                id="voice-record-button",
                                                icon=DashIconify(
                                                    id="voice-record-icon",
                                                    icon="proicons:microphone",
                                                    width=20,
                                                    height=20
                                                ),
                                                type="primary",
                                                size="large",
                                                title="开始录音",
                                                style=style(
                                                    padding="8px",
                                                    width="40px",
                                                    height="40px",
                                                    borderRadius="8px",
                                                    backgroundColor="#dc2626",
                                                    borderColor="#dc2626",
                                                    boxShadow="0 2px 4px rgba(220, 38, 38, 0.2)"
                                                ),
                                                # 🔧 响应式：小屏幕（<576px）时隐藏，通过className控制
                                                className="voice-button-desktop"
                                            )
                                        ] if enable_voice_input else [] ),

                                        # 通话按钮 - 统一样式，大屏幕（≥576px）时显示在第一行
                                        *( [
                                            fac.AntdButton(
                                                id="voice-call-btn",
                                                icon=DashIconify(
                                                    icon="bi:telephone",
                                                    rotate=2,
                                                    width=20,
                                                    height=20
                                                ),
                                                type="primary",
                                                size="large",
                                                title="实时语音通话",
                                                style=style(
                                                    padding="8px",
                                                    width="40px",
                                                    height="40px",
                                                    borderRadius="8px",
                                                    backgroundColor="#52c41a",
                                                    borderColor="#52c41a",
                                                    boxShadow="0 2px 4px rgba(82, 196, 26, 0.2)"
                                                ),
                                                # 🔧 响应式：小屏幕（<576px）时隐藏，通过className控制
                                                className="voice-button-desktop"
                                            )
                                        ] if enable_voice_input else [] )
                                    ],
                                    size="small"
                                )
                            )
                        ],
                        align="middle",
                        gutter=0,
                        style=style(width="100%")
                    ),
                    
                    # 第二行：录音按钮 + 通话按钮（仅在 < 576px 时显示，各占50%宽度）
                    *( [
                        fac.AntdRow(
                            [
                                # 录音按钮 - 小屏幕时显示，占50%宽度
                                fac.AntdCol(
                                    span=12,  # 占50%（24格系统中的12格）
                                    children=fac.AntdButton(
                                        id="voice-record-button-mobile",
                                        icon=DashIconify(
                                            id="voice-record-icon-mobile",
                                            icon="proicons:microphone",
                                            width=20,
                                            height=20
                                        ),
                                        type="primary",
                                        size="large",
                                        title="开始录音",
                                        block=True,  # 占满整列宽度
                                        style=style(
                                            padding="8px",
                                            height="40px",
                                            borderRadius="8px",
                                            backgroundColor="#dc2626",
                                            borderColor="#dc2626",
                                            boxShadow="0 2px 4px rgba(220, 38, 38, 0.2)"
                                        ),
                                        className="voice-button-mobile"
                                    )
                                ),
                                # 通话按钮 - 小屏幕时显示，占50%宽度
                                fac.AntdCol(
                                    span=12,  # 占50%（24格系统中的12格）
                                    children=fac.AntdButton(
                                        id="voice-call-btn-mobile",
                                        icon=DashIconify(
                                            icon="bi:telephone",
                                            rotate=2,
                                            width=20,
                                            height=20
                                        ),
                                        type="primary",
                                        size="large",
                                        title="实时语音通话",
                                        block=True,  # 占满整列宽度
                                        style=style(
                                            padding="8px",
                                            height="40px",
                                            borderRadius="8px",
                                            backgroundColor="#52c41a",
                                            borderColor="#52c41a",
                                            boxShadow="0 2px 4px rgba(82, 196, 26, 0.2)"
                                        ),
                                        className="voice-button-mobile"
                                    )
                                )
                            ],
                            gutter=[8, 0],  # 左右间距8px
                            style=style(
                                width="100%",
                                marginTop="8px"
                            ),
                            className="voice-buttons-row-mobile"
                        )
                    ] if enable_voice_input else [] )
                ],
                # 统一外框样式
                id="chat-input-container",
                style=style(
                    border="1px solid #d9d9d9",
                    borderRadius="6px",
                    padding="4px 6px",
                    backgroundColor="#fff",
                    transition="all 0.3s",
                    hover={"border-color": "#40a9ff"}
                )
            )
            
            # 注意：不包含底部提示，按要求已移除
        ],
        style=style(
            padding="16px 24px",
            backgroundColor="#fff",
            borderTop="1px solid #f0f0f0"
        )
    )
    return children