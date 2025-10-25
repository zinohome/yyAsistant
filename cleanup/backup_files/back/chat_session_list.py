import feffery_utils_components as fuc
import feffery_antd_components as fac
from dash_iconify import DashIconify
from feffery_dash_utils.style_utils import style


def render(sessions=None, search_placeholder="搜索会话内容", collapsed=False):
    """渲染聊天会话列表组件
    
    参数:
        sessions (list, optional): 会话数据列表，每个会话包含key, title, time, content, unread字段
        search_placeholder (str, optional): 搜索框占位符文本
        collapsed (bool, optional): 是否折叠会话列表，默认为False
    
    返回:
        Dash组件对象
    """
    
    # 默认会话数据
    default_sessions = [
        {"key": "1", "title": "如何使用Dash框架", "time": "10:30", "content": "Dash是一个用于构建分析型Web应用的Python框架...", "unread": 0},
        {"key": "2", "title": "数据可视化最佳实践", "time": "昨天", "content": "数据可视化需要考虑用户体验和数据准确性...", "unread": 0},
        {"key": "3", "title": "Python性能优化技巧", "time": "周一", "content": "使用生成器、避免全局变量、利用内置函数...", "unread": 0}
    ]
    
    # 使用传入的会话数据或默认数据
    session_data = sessions if sessions else default_sessions
    
    if collapsed:
        # 折叠状态：只显示展开图标，并确保其在顶部位置，与非折叠状态保持一致的顶部距离
        return [
            fuc.FefferyDiv(
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdButton(
                                icon=fac.AntdIcon(icon="antd-menu-unfold"),
                                id="ai-chat-x-collapse-sessions",
                                type="text",
                                style=style(
                                    padding="4px",
                                    position="relative",  # 相对定位
                                    left="-4px"  # 向左微调，解决偏右问题
                                ),
                                title="展开会话列表"
                            ),
                            flex="none"
                        )
                    ],
                    justify="center",  # 确保图标居中显示，不被边框挡住
                    style=style(paddingRight="0px", paddingLeft="0px")
                ),
                style=style(marginBottom="8px", paddingTop="4px", paddingLeft="0px", paddingRight="0px")
            )
        ]

    return [
        # 折叠按钮区域 - 使用FefferyDiv统一容器
        fuc.FefferyDiv(
            fac.AntdRow(
                [
                    fac.AntdCol(
                        flex="auto"
                    ),
                    fac.AntdCol(
                        fac.AntdButton(
                            icon=fac.AntdIcon(icon="antd-menu-fold"),
                            id="ai-chat-x-collapse-sessions",
                            type="text",
                            style=style(padding="4px"),
                            title="折叠会话列表"
                        ),
                        flex="none"
                    )
                ],
                justify="end",
                style=style(paddingRight="8px")
            ),
            style=style(marginBottom="8px", paddingTop="4px")  # 添加相同的顶部内边距
        ),
                
        # 新的会话按钮区域 - 使用FefferyDiv统一容器
        fuc.FefferyDiv(
            [
                fac.AntdIcon(icon="antd-plus", style=style(marginRight="8px", color="#1677ff")),
                fac.AntdText('新的会话', style=style(color="#1677ff"))
            ],
            id="ai-chat-x-new-session",
            style=style(
                display="flex",
                alignItems="center",
                justifyContent="center",
                backgroundColor="#1677ff10",  # 转换自 rgba(22, 119, 255, 0.06)
                border="1px solid #1677ff34",  # 转换自 rgba(22, 119, 255, 0.204)
                borderRadius="6px",
                padding="8px 0",
                cursor="pointer",
                transition="all 0.2s ease",  # 平滑过渡
            ),
            shadow="hover-shadow-light",
            enableEvents=['click', 'hover']
        ),

        # 会话列表区域 - 保持FefferyDiv容器
        fuc.FefferyDiv(
            [
                fac.AntdSpace(
                    [
                        # 将AntdCard替换为FefferyDiv
                        fuc.FefferyDiv(
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        fac.AntdText(
                                            item["title"], 
                                            strong=True,
                                            ellipsis=True,
                                            style=style(padding="12px 0")
                                        ),
                                        flex="auto"
                                    ),
                                    fac.AntdCol(
                                        # 添加下拉菜单
                                        fac.AntdDropdown(
                                            fac.AntdButton(
                                                icon=fac.AntdIcon(
                                                    icon="antd-more",
                                                    className="global-help-text",
                                                ),
                                                type="text",
                                                size="small",
                                                style=style(color="#8c8c8c")  # 设置按钮颜色为灰色
                                            ),
                                            id={"type": "ai-chat-x-session-dropdown", "index": item["key"]},
                                            menuItems=[
                                                {
                                                    "title": "改名",
                                                    "key": "rename",
                                                    "icon": "antd-edit"  # 添加改名图标
                                                },
                                                {
                                                    "title": "删除",
                                                    "key": "delete",
                                                    "icon": "antd-delete"  # 添加删除图标
                                                }
                                            ],
                                            trigger="click",
                                        ),
                                        flex="none"
                                    )
                                ],
                                align="middle"
                            ),
                            id={"type": "ai-chat-x-session-item", "index": item["key"]},
                            style=style(
                                #border="1px solid #f0f0f0",
                                borderRadius="6px",
                                padding="0 12px",
                                marginBottom="4px",  # 将间距从8px改为4px
                                cursor="pointer",
                                backgroundColor="#fafafa"  # 设置浅灰色背景
                                #**({"backgroundColor": "#e6f7ff", "borderColor": "#bae7ff"} if item["key"] == "1" else {})
                            ),
                            enableEvents=['click', 'hover'],
                            shadow="hover-shadow"
                        )
                        for item in session_data
                    ],
                    id="ai-chat-x-session-list",
                    direction="vertical",
                    style=style(width="100%")
                )
            ],
            style=style(height="calc(100% - 52px)", overflow="auto", padding="8px")
        )
    ]