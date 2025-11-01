class AuthConfig:
    """用户鉴权配置参数"""

    # 角色权限类别
    roles: dict = {
        "admin": {
            "description": "系统管理员",
        },
        "normal": {
            "description": "常规用户",
        },
    }

    # 常规用户角色
    normal_role: str = "normal"

    # 管理员角色
    admin_role: str = "admin"

    # 不同角色权限页面可访问性规则，其中'include'模式下自动会纳入首页，无需额外设置
    # type：规则类型，可选项有'all'（可访问全部页面）、'include'（可访问指定若干页面）、'exclude'（不可访问指定若干页面）
    # keys：受type字段影响，定义可访问的指定若干页面/不可访问的指定若干页面，所对应RouterConfig.core_side_menu中菜单结构的key值
    pathname_access_rules: dict = {
        "admin": {"type": "all"},
        "normal": {
            "type": "exclude",
            "keys": [
                # 常规用户禁止访问系统管理相关页面
                "/core/login-logs",
                "/core/users",
                "/core/other-page1",
                "/core/page1",
                "/core/url-params-page",
                "/core/independent-page",
                "/core/independent-wildcard-page",
                "/core/sub-menu-page1",
                "/core/sub-menu-page2",
                "/core/sub-menu-page3",
            ],
        },
        # "normal": {"type": "include", "keys": ["/core/page2", "/core/page5"]},
    }

    # 普通用户允许访问的页面列表
    # 普通用户只能访问此列表中的页面，其他页面将自动重定向到配置的重定向目标页面
    normal_user_allowed_pathnames: list = [
        "/core/chat",
    ]

    # 普通用户访问未授权页面时的重定向目标
    normal_user_redirect_pathname: str = "/core/chat"
