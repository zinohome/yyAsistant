import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style


def render(sessions=None, search_placeholder="搜索会话内容"):
    """渲染聊天会话列表组件
    
    参数:
        sessions (list, optional): 会话数据列表，每个会话包含key, title, time, content, unread字段
        search_placeholder (str, optional): 搜索框占位符文本
    
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
    
    return [
        # 搜索框区域
        fac.AntdInput(
            id="ai-chat-x-session-search",
            placeholder=search_placeholder,
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
                            size="small",
                            hoverable=True,
                            id={"type": "ai-chat-x-session-item", "index": item["key"]},
                            styles={'header': {'display': 'none'}},
                            style=style(marginBottom="8px", cursor="pointer")
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