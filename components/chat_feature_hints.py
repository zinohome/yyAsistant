import feffery_antd_components as fac
import feffery_utils_components as fuc  # 导入FefferyDiv所在的模块
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
                # 使用FefferyDiv替换AntdCard
                fuc.FefferyDiv(
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
                    style=style(
                        borderRadius="8px",
                        padding="12px",
                        maxWidth="70%",
                        backgroundColor="#f0f8ff",
                        # 添加FefferyDiv特有的属性
                        shadow="always-shadow-light",  # 始终显示浅色阴影效果
                        scrollbar="simple"  # 如果内容过长，使用简洁的滚动条
                    )
                ),
                flex="auto",
                style=style(textAlign="left")
            )
        ],
        style=style(marginBottom="16px", padding="0 24px")
    )