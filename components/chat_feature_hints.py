import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style


def render(
    hints=["询问技术问题", "获取设计建议", "寻求代码帮助"],
    hint_colors=["blue", "purple", "green"],
    prefix="💡 您可以："
):
    """
    聊天功能提示卡片组件
    
    参数:
        hints: 功能提示列表
        hint_colors: 提示标签颜色列表
        prefix: 提示前缀文本
    
    返回:
        功能提示卡片组件的渲染结果
    """
    
    return fac.AntdRow(
        [
            fac.AntdCol(
                flex="none",
                style=style(marginRight="12px")
            ),
            fac.AntdCol(
                fac.AntdCard(
                    [
                        fac.AntdText(prefix, type="secondary"),
                        fac.AntdSpace(
                            [
                                fac.AntdTag(hint, color=color, bordered=False)
                                for hint, color in zip(hints, hint_colors)
                            ],
                            direction="vertical",
                            style=style(width="100%")
                        )
                    ],
                    size="small",
                    variant='borderless',
                    styles={'header': {'display': 'none'}},
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