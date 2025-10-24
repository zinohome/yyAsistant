
import dash
import uuid
from dash import html
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output
from dash.dependencies import ClientsideFunction
from server import app




# 同时修改render_my_info_drawer函数，移除固定宽度设置
def render_my_info_drawer():
    return fac.AntdDrawer(
        id="my-info-drawer",
        title=[
            fac.AntdIcon(icon="antd-user"),
            fac.AntdText("健康档案")
        ],
        # 移除固定宽度，由回调函数动态设置
        children=[
            html.Div(id="my-info-content")
        ]
    )


@app.callback(
    Output("my-info-content", "children"),
    Input("my-info-drawer", "visible"),
    prevent_initial_call=True,
)
def update_drawer_content(visible):
    if visible:
        return html.Div(
            [
                # 顶部标题栏
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdText("健康档案管理", strong=True, style={'fontSize': '18px'})
                        ),
                        fac.AntdCol(
                            fac.AntdButton(
                                "编辑资料",
                                type="primary",
                                size="small",
                                style={'float': 'right'}
                            )
                        )
                    ],
                    style={'marginBottom': '24px', 'padding': '16px 0'}
                ),
                
                # 用户头像和欢迎卡片区域
                fac.AntdSpace(
                    [
                        # 用户头像
                        fac.AntdAvatar(
                            icon='antd-user',
                            style={'width': 80, 'height': 80, 'backgroundColor': '#1890ff'}
                        ),
                        
                        # 欢迎卡片
                        fac.AntdCard(
                            [
                                fac.AntdText("欢迎来到健康档案", strong=True, style={'fontSize': '16px'}),
                                fac.AntdDivider(style={'margin': '8px 0'}),
                                # 使用 style 和 marginLeft: 'auto' 替代 justify="between"
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("今日步数是否达标"),
                                        fac.AntdText("***步", type="secondary")
                                    ],
                                    style={'width': '100%'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("授权查看运动健康"),
                                        fac.AntdButton("去授权 >", type="text")
                                    ],
                                    style={'width': '100%'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("我的健康记录"),
                                        fac.AntdText("***条", type="secondary")
                                    ],
                                    style={'width': '100%'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("填写健康史"),
                                        fac.AntdButton("去填写 >", type="text")
                                    ],
                                    style={'width': '100%'}
                                )
                            ],
                            style={'width': '100%', 'backgroundColor': '#f0f8ff'}
                        )
                    ],
                    style={'width': '100%', 'marginBottom': '16px'}
                ),
                
                # AI助手提示
                fac.AntdCard(
                    fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon='antd-robot', style={'color': '#1890ff'}),
                                    fac.AntdText("感冒灵颗粒有哪些副作用"),
                                    fac.AntdButton("去问问 >", type="text")
                                ],
                                style={'width': '100%'}
                            ),
                    style={'marginBottom': '16px', 'backgroundColor': '#fafafa'}
                ),
                
                # 底部导航栏
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            flex=1,
                            children=fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-file-text"),
                                    fac.AntdText("就医资料夹")
                                ],
                                direction="vertical",
                                style={'textAlign': 'center', 'padding': '12px', 'borderBottom': '2px solid #1890ff', 'color': '#1890ff'}
                            )
                        ),
                        fac.AntdCol(
                            flex=1,
                            children=fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-calendar"),
                                    fac.AntdText("就诊记录")
                                ],
                                direction="vertical",
                                style={'textAlign': 'center', 'padding': '12px', 'borderBottom': '2px solid #f0f0f0'}
                            )
                        ),
                        fac.AntdCol(
                            flex=1,
                            children=fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-heart"),
                                    fac.AntdText("体检报告")
                                ],
                                direction="vertical",
                                style={'textAlign': 'center', 'padding': '12px', 'borderBottom': '2px solid #f0f0f0'}
                            )
                        ),
                        fac.AntdCol(
                            flex=1,
                            children=fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-pie-chart"),
                                    fac.AntdText("健康数据")
                                ],
                                direction="vertical",
                                style={'textAlign': 'center', 'padding': '12px', 'borderBottom': '2px solid #f0f0f0'}
                            )
                        ),
                        fac.AntdCol(
                            flex=1,
                            children=fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-user"),
                                    fac.AntdText("个人资料")
                                ],
                                direction="vertical",
                                style={'textAlign': 'center', 'padding': '12px', 'borderBottom': '2px solid #f0f0f0'}
                            )
                        )
                    ],
                    style={'marginBottom': '16px'}
                ),
                
                # 健康数据卡片
                fac.AntdCard(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    flex=1,
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("今日步数", type="secondary"),
                                            fac.AntdText("8,234", strong=True, style={'fontSize': '24px'})
                                        ],
                                        direction="vertical",
                                        style={'textAlign': 'center'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex=1,
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("睡眠时长", type="secondary"),
                                            fac.AntdText("6.5h", strong=True, style={'fontSize': '24px'})
                                        ],
                                        direction="vertical",
                                        style={'textAlign': 'center'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex=1,
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("卡路里消耗", type="secondary"),
                                            fac.AntdText("456kcal", strong=True, style={'fontSize': '24px'})
                                        ],
                                        direction="vertical",
                                        style={'textAlign': 'center'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex=1,
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("心率", type="secondary"),
                                            fac.AntdText("78bpm", strong=True, style={'fontSize': '24px'})
                                        ],
                                        direction="vertical",
                                        style={'textAlign': 'center'}
                                    )
                                )
                            ]
                        )
                    ],
                    style={'marginBottom': '16px'}
                ),
                
                # 健康史内容区域
                fac.AntdSpace(
                    [
                        # 家族史
                        fac.AntdCard(
                            [
                                fac.AntdRow(
                                    [
                                        fac.AntdCol(
                                            flex='auto',
                                            children=fac.AntdText("家族史", strong=True)
                                        ),
                                        fac.AntdCol(
                                            children=fac.AntdButton("编辑 >", type="text", style={'fontSize': '12px'})
                                        )
                                    ],
                                    align='middle',
                                    style={'marginBottom': '16px'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag(color="blue", style={'margin': '0 8px 0 0'}),
                                        fac.AntdText("家族疾病"),
                                        fac.AntdText("待补充", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    style={'width': '100%', 'marginBottom': '8px'}
                                )
                            ],
                            style={'width': '100%', 'marginBottom': '8px'}
                        ),
                        
                        # 个人史
                        fac.AntdCard(
                            [
                                fac.AntdRow(
                                    [
                                        fac.AntdCol(
                                            flex='auto',
                                            children=fac.AntdText("个人史", strong=True)
                                        ),
                                        fac.AntdCol(
                                            children=fac.AntdButton("编辑 >", type="text", style={'fontSize': '12px'})
                                        )
                                    ],
                                    align='middle',
                                    style={'marginBottom': '16px'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag(color="blue", style={'margin': '0 8px 0 0'}),
                                        fac.AntdText("饮酒情况"),
                                        fac.AntdText("待补充", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    style={'width': '100%', 'marginBottom': '8px'}
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag(color="blue", style={'margin': '0 8px 0 0'}),
                                        fac.AntdText("吸烟情况"),
                                        fac.AntdText("待补充", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    style={'width': '100%'}
                                )
                            ],
                            style={'width': '100%'}
                        )
                    ],
                    direction="vertical",
                    style={'width': '100%'}
                )
            ],
            style={'marginBottom': 0, 'backgroundColor': '#fff'}
        )
    return dash.no_update


#  在文件末尾添加以下代码
app.clientside_callback(
    ClientsideFunction(
        namespace="clientside_basic",
        function_name="handleResponsiveDrawerWidth"
    ),
    Output("my-info-drawer", "width"),
    Input("my-info-drawer", "visible"),
    prevent_initial_call=False
)