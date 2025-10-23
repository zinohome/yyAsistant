import feffery_utils_components as fuc
import feffery_antd_components as fac
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style
from configs.topics_loader import get_category_topics, get_settings


def render(
    placeholder="输入您的问题...",
    max_length=2000,
    topics=None,
    icons=None,
    enable_file_upload=True,
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
    
    # 统一外框的输入区域容器
    children =  fuc.FefferyDiv(
        [
            # 话题提示栏 - 替代工具栏
            fuc.FefferyDiv(
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
            ),
            
            # 输入框区域 - 包含统一外框
            fuc.FefferyDiv(
                [
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
                                    showCount=True,
                                    maxLength=max_length,
                                    variant='borderless',
                                    styles={
                                        'textarea': {
                                            'transition': 'none',
                                            'animation': 'none',
                                            'resize': 'none'
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
                            
                            # 右侧按钮组
                            fac.AntdCol(
                                flex="none",
                                children=fac.AntdSpace(
                                    [   
                                        # 发送按钮（上箭头） - 统一样式
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

                                        # 录音按钮 - 统一样式
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
                                                )
                                            )
                                        ] if enable_voice_input else [] ),

                                        # 通话按钮 - 统一样式
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
                                                )
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
                    )
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