import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style


def render(
    placeholder="输入您的问题...",
    max_length=2000,
    topics=["如何提高工作效率", "数据分析技巧", "代码优化建议", "项目管理方法"],
    icons=["fluent-mdl2:web-components", "fluent-mdl2:activate-orders", "fluent-mdl2:add-in", "fluent-mdl2:company-directory-mirrored"],
    enable_file_upload=True,
    enable_voice_input=True,
    enable_send_button=True
):
    """
    聊天输入区域组件 - 支持话题提示、附件上传、语音输入等功能
    
    参数:
        placeholder: 输入框占位文本
        max_length: 最大输入长度
        topics: 话题提示列表
        icons: 话题图标列表，与topics一一对应
        enable_file_upload: 是否启用文件上传
        enable_voice_input: 是否启用语音输入
        enable_send_button: 是否启用发送按钮
    """
    
    # 统一外框的输入区域容器
    return fuc.FefferyDiv(
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
                                id=f"chat-topic-{index}",
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
                                ),
                                enableEvents=['click', 'hover'],
                                # 点击事件，暂时置空
                                nClicks=0

                            ) for index, topic in enumerate(topics)
                        ],
                        wrap=True,
                        style=style(width="100%")
                    )
                ],
                style=style(marginBottom="8px")
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
                                    placeholder=placeholder,
                                    autoSize={"minRows": 3, "maxRows": 6},
                                    showCount=True,
                                    maxLength=max_length,
                                    variant='borderless',
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
                                        # 录音按钮
                                        *( [
                                            fac.AntdButton(
                                                #icon=fac.AntdIcon(icon="proicons:microphone"),
                                                icon=DashIconify(icon="proicons:microphone",
                                                        width=25,
                                                        height=25,
                                                        rotate=0,
                                                        flip="horizontal",
                                                    ),
                                                type="text",
                                                title="语音输入",
                                                style=style(padding="4px 8px")
                                            )
                                        ] if enable_voice_input else [] ),

                                        # 通话按钮
                                        *( [
                                            fac.AntdButton(
                                                #icon=fac.AntdIcon(icon="proicons:microphone"),
                                                icon=DashIconify(icon="bi:telephone",
                                                        width=25,
                                                        height=25,
                                                        rotate=3,
                                                        flip="horizontal",
                                                    ),
                                                type="text",
                                                title="直接通话",
                                                style=style(padding="4px 8px")
                                            )
                                        ] if enable_voice_input else [] ),
                                        
                                        # 发送按钮（上箭头）
                                        *( [
                                            fac.AntdButton(
                                                icon=fac.AntdIcon(icon="antd-arrow-up"),
                                                id="ai-chat-x-send-btn",
                                                type="primary",
                                                shape="circle",
                                                style=style(
                                                    padding="0"
                                                )
                                            )
                                        ] if enable_send_button else [] )
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