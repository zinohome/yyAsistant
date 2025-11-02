import feffery_utils_components as fuc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from dash import html

from configs import BaseConfig, LayoutConfig

# 令绑定的回调函数子模块生效
import callbacks.login_c  # noqa: F401


def render():
    """渲染用户登录页面"""

    return fac.AntdRow(
        [
            # 左侧半边
            fac.AntdCol(
                [
                    fuc.FefferyMotion(
                        html.Img(
                            src="/assets/imgs/login/插图1.svg",
                            style=style(width="25vw"),
                        ),
                        style={
                            "position": "absolute",
                            "left": "10%",
                            "top": "15%",
                            "rotateZ": "-5deg",
                        },
                        animate={"y": [25, -25, 25]},
                        transition={
                            "duration": 4.5,
                            "repeat": "infinity",
                            "type": "spring",
                        },
                    ),
                    fuc.FefferyMotion(
                        html.Img(
                            src="/assets/imgs/login/插图2.svg",
                            style=style(width="15vw"),
                        ),
                        style={
                            "position": "absolute",
                            "right": "20%",
                            "top": "25%",
                            "rotateZ": "15deg",
                        },
                        animate={"y": [-15, 15, -15]},
                        transition={
                            "duration": 5.5,
                            "repeat": "infinity",
                            "type": "spring",
                        },
                    ),
                    fuc.FefferyMotion(
                        html.Img(
                            src="/assets/imgs/login/插图3.svg",
                            style=style(width="12vw"),
                        ),
                        style={
                            "position": "absolute",
                            "left": "25%",
                            "bottom": "25%",
                            "rotateZ": "-8deg",
                        },
                        animate={"y": [10, -10, 10]},
                        transition={
                            "duration": 5,
                            "repeat": "infinity",
                            "type": "spring",
                        },
                    ),
                    fuc.FefferyMotion(
                        html.Img(
                            src="/assets/imgs/login/插图4.svg",
                            style=style(width="25vw"),
                        ),
                        style={
                            "position": "absolute",
                            "right": "15%",
                            "bottom": "8%",
                            "rotateZ": "5deg",
                        },
                        animate={"y": [20, -20, 20]},
                        transition={
                            "duration": 6,
                            "repeat": "infinity",
                            "type": "spring",
                        },
                    ),
                ]
                if LayoutConfig.login_left_side_content_type == "image"
                else [
                    html.Video(
                        src="/assets/videos/login-bg.mp4",
                        autoPlay=True,
                        muted=True,
                        loop=True,
                        style=style(
                            width="100%",
                            height="100%",
                            position="absolute",
                            objectFit="cover",
                            borderTopRightRadius=12,
                            borderBottomRightRadius=12,
                            pointerEvents="none",
                        ),
                    )
                ],
                xs=0,  # 超小屏幕隐藏左侧
                sm=0,  # 小屏幕隐藏左侧
                md=14, # 中等屏幕及以上显示左侧
                style=style(position="relative", height="100vh"),
                className="login-left-side",
            ),
            # 右侧半边
            fac.AntdCol(
                fac.AntdCenter(
                    [
                        fac.AntdSpace(
                            [
                                html.Img(
                                    src="/assets/imgs/girl-login.ico",
                                    height=96,
                                ),
                                fac.AntdText(
                                    BaseConfig.app_title,
                                    style=style(fontSize=36),
                                ),
                                fac.AntdForm(
                                    [
                                        fac.AntdFormItem(
                                            fac.AntdInput(
                                                id="login-user-name",
                                                placeholder="请输入用户名",
                                                size="large",
                                                prefix=fac.AntdIcon(
                                                    icon="antd-user",
                                                    className="global-help-text",
                                                ),
                                                autoComplete="off",
                                            ),
                                            label="用户名",
                                        ),
                                        fac.AntdFormItem(
                                            fac.AntdInput(
                                                id="login-password",
                                                placeholder="请输入密码",
                                                size="large",
                                                mode="password",
                                                prefix=fac.AntdIcon(
                                                    icon="antd-lock",
                                                    className="global-help-text",
                                                ),
                                            ),
                                            label="密码",
                                        ),
                                        fac.AntdCheckbox(
                                            id="login-remember-me", label="记住我"
                                        ),
                                        fac.AntdButton(
                                            "登录",
                                            id="login-button",
                                            loadingChildren="校验中",
                                            type="primary",
                                            block=True,
                                            size="large",
                                            style=style(marginTop=18),
                                        ),
                                    ],
                                    id="login-form",
                                    enableBatchControl=True,
                                    layout="vertical",
                                    style=style(width={
                                        'xs': '100%',  # 小屏幕下宽度自适应
                                        'sm': '85%',   # 平板下宽度85%
                                        'md': 350      # 桌面端固定宽度350px
                                    }),
                                ),
                            ],
                            direction="vertical",
                            align="center",
                        )
                    ],
                    style=style(height="calc(100% - 200px)"),
                ),
                # 修改响应式布局
                xs=24,  # 超小屏幕占满24格
                sm=24,  # 小屏幕占满24格
                md=10,  # 中等屏幕及以上保持10格
                className="login-right-side",
            ),
        ],
        wrap=True,  # 允许换行以适应小屏幕
        style=style(height="100vh", minHeight=600),
    )
