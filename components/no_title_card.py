"""
无标题卡片组件

提供一个便捷函数来创建隐藏了 title 区域的 AntdCard，以节省页面空间
"""
import feffery_antd_components as fac


def NoTitleCard(*args, **kwargs):
    """
    创建无标题卡片组件的便捷函数
    
    这个函数会创建一个隐藏了 header 和 title 区域的 AntdCard，
    从而节省页面空间。
    
    参数：
        *args: 位置参数，通常是 children
        **kwargs: 关键字参数，所有 AntdCard 支持的参数
    
    返回：
        fac.AntdCard 实例，但 header 和 title 区域已隐藏
    """
    # 获取原始 styles 参数
    original_styles = kwargs.get('styles', {})
    if not isinstance(original_styles, dict):
        original_styles = {}
    
    # 创建新的 styles，隐藏 header 和 title 区域
    new_styles = {
        **original_styles,
        'header': {
            **original_styles.get('header', {}),
            'display': 'none'
        },
        'title': {
            **original_styles.get('title', {}),
            'display': 'none'
        }
    }
    
    # 更新 kwargs
    kwargs['styles'] = new_styles
    
    # 如果有位置参数，将其作为 children
    if args:
        kwargs['children'] = args[0] if len(args) == 1 else list(args)
    
    # 返回 AntdCard 实例
    return fac.AntdCard(**kwargs)

