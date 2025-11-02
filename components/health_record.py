
import dash
from dash import html
import feffery_antd_components as fac
from dash.dependencies import Input, Output
from dash.dependencies import ClientsideFunction
from server import app
from components.no_title_card import NoTitleCard


def render_health_record_drawer():
    """渲染健康档案抽屉组件"""
    return fac.AntdDrawer(
        id="health-record-drawer",
        title=[
            fac.AntdIcon(icon="antd-user"),
            fac.AntdText("健康档案")
        ],
        # 移除固定宽度，由回调函数动态设置
        children=[
            html.Div(id="health-record-content")
        ]
    )


@app.callback(
    Output("health-record-content", "children"),
    Input("health-record-drawer", "visible"),
    prevent_initial_call=True,
)
def update_drawer_content(visible):
    """更新抽屉内容"""
    if visible:
        return html.Div(
            [
                # 顶部用户信息区域
                html.Div(
                    _render_user_header(),
                    style={'padding': '16px', 'marginBottom': '16px'}
                ),
                
                # Tab标签页内容
                html.Div(
                    fac.AntdTabs(
                        id="health-record-tabs",
                        items=[
                            {
                                "key": "health_check",
                                "label": "健康自测",
                                "children": _render_health_check_tab()
                            },
                            {
                                "key": "health_history",
                                "label": "健康史",
                                "children": _render_health_history_tab()
                            },
                            {
                                "key": "diet_health",
                                "label": "饮食健康",
                                "children": _render_diet_health_tab()
                            },
                            {
                                "key": "exercise_health",
                                "label": "运动健康",
                                "children": _render_exercise_health_tab()
                            },
                            {
                                "key": "medication_record",
                                "label": "药物记录",
                                "children": _render_medication_record_tab()
                            },
                            {
                                "key": "medical_folder",
                                "label": "就医资料夹",
                                "children": _render_medical_folder_tab()
                            }
                        ],
                        defaultActiveKey="health_check"
                    ),
                    style={'padding': '0 16px 16px 16px', 'backgroundColor': '#fff'}
                )
            ],
            style={'backgroundColor': '#fff'}
        )
    return dash.no_update


def _render_user_header():
    """渲染顶部用户信息区域"""
    return NoTitleCard(
        [
            fac.AntdRow(
                [
                    # 左侧：人物头像
                    fac.AntdCol(
                        flex="none",
                        children=html.Div(
                            html.Img(
                                src="/assets/imgs/people.png",
                                style={
                                    'width': '100%',
                                    'height': 'auto',
                                    'maxWidth': '140px',
                                    'maxHeight': '140px',
                                    'borderRadius': '8px',
                                    'objectFit': 'contain',
                                    'display': 'block'
                                }
                            ),
                            style={
                                'width': '120px',
                                'height': '120px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'overflow': 'hidden'
                            }
                        )
                    ),
                    # 右侧：用户信息
                    fac.AntdCol(
                        flex="auto",
                        children=html.Div(
                            fac.AntdSpace(
                                [
                                    fac.AntdText("张**", strong=True, style={'fontSize': '20px'}),
                                    fac.AntdDivider(direction="vertical"),
                                    fac.AntdText("男", type="secondary"),
                                    fac.AntdDivider(direction="vertical"),
                                    fac.AntdText("65岁", type="secondary"),
                                    fac.AntdDivider(direction="vertical"),
                                    fac.AntdText("身份证：320***********1234", type="secondary"),
                                    fac.AntdButton("编辑资料", type="link", size="small", style={'marginLeft': 'auto'})
                                ],
                                direction="horizontal",
                                style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                            ),
                            style={'display': 'flex', 'alignItems': 'center', 'minHeight': '120px'}
                        )
                    )
                ],
                align="middle",
                gutter=16,
                wrap=False
            )
        ],
        style={'marginBottom': '0'}
    )


def _render_medical_folder_tab():
    """渲染就医资料夹Tab内容"""
    return html.Div(
        [
            fac.AntdSpace(
                [
                    fac.AntdButton("上传资料", type="primary", icon=fac.AntdIcon(icon="antd-upload")),
                    fac.AntdButton("新建文件夹", type="default", icon=fac.AntdIcon(icon="antd-folder-add"))
                ],
                style={'marginBottom': '16px', 'width': '100%', 'justifyContent': 'flex-end'}
            ),
            # 文件列表
            html.Div(
                [
                    html.Div(
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    flex="none",
                                    children=fac.AntdIcon(
                                        icon="antd-file-pdf",
                                        style={'fontSize': '24px', 'color': '#1890ff', 'marginRight': '12px'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex="auto",
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("2024年体检报告.pdf", strong=True),
                                            fac.AntdTag("体检报告", color="blue"),
                                            fac.AntdText("体检日期：2024-03-15 | 大小：2.3MB", type="secondary"),
                                            fac.AntdSpace(
                                                [
                                                    fac.AntdButton("查看", type="link", size="small"),
                                                    fac.AntdButton("下载", type="link", size="small"),
                                                    fac.AntdButton("删除", type="link", size="small", danger=True)
                                                ],
                                                style={'marginLeft': 'auto'}
                                            )
                                        ],
                                        direction="horizontal",
                                        style={'width': '100%', 'alignItems': 'center'}
                                    )
                                )
                            ],
                            align="middle"
                        ),
                        style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                    ),
                    html.Div(
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    flex="none",
                                    children=fac.AntdIcon(
                                        icon="antd-file-image",
                                        style={'fontSize': '24px', 'color': '#1890ff', 'marginRight': '12px'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex="auto",
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("X光片-胸部检查.jpg", strong=True),
                                            fac.AntdTag("影像资料", color="blue"),
                                            fac.AntdText("检查日期：2024-02-20 | 大小：5.6MB", type="secondary"),
                                            fac.AntdSpace(
                                                [
                                                    fac.AntdButton("查看", type="link", size="small"),
                                                    fac.AntdButton("下载", type="link", size="small"),
                                                    fac.AntdButton("删除", type="link", size="small", danger=True)
                                                ],
                                                style={'marginLeft': 'auto'}
                                            )
                                        ],
                                        direction="horizontal",
                                        style={'width': '100%', 'alignItems': 'center'}
                                    )
                                )
                            ],
                            align="middle"
                        ),
                        style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                    ),
                    html.Div(
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    flex="none",
                                    children=fac.AntdIcon(
                                        icon="antd-file-pdf",
                                        style={'fontSize': '24px', 'color': '#1890ff', 'marginRight': '12px'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex="auto",
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("血常规检查报告.pdf", strong=True),
                                            fac.AntdTag("检查报告", color="blue"),
                                            fac.AntdText("检查日期：2024-01-10 | 大小：856KB", type="secondary"),
                                            fac.AntdSpace(
                                                [
                                                    fac.AntdButton("查看", type="link", size="small"),
                                                    fac.AntdButton("下载", type="link", size="small"),
                                                    fac.AntdButton("删除", type="link", size="small", danger=True)
                                                ],
                                                style={'marginLeft': 'auto'}
                                            )
                                        ],
                                        direction="horizontal",
                                        style={'width': '100%', 'alignItems': 'center'}
                                    )
                                )
                            ],
                            align="middle"
                        ),
                        style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                    ),
                    html.Div(
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    flex="none",
                                    children=fac.AntdIcon(
                                        icon="antd-file-word",
                                        style={'fontSize': '24px', 'color': '#1890ff', 'marginRight': '12px'}
                                    )
                                ),
                                fac.AntdCol(
                                    flex="auto",
                                    children=fac.AntdSpace(
                                        [
                                            fac.AntdText("病历记录.docx", strong=True),
                                            fac.AntdTag("病历", color="blue"),
                                            fac.AntdText("就诊日期：2023-12-05 | 大小：1.2MB", type="secondary"),
                                            fac.AntdSpace(
                                                [
                                                    fac.AntdButton("查看", type="link", size="small"),
                                                    fac.AntdButton("下载", type="link", size="small"),
                                                    fac.AntdButton("删除", type="link", size="small", danger=True)
                                                ],
                                                style={'marginLeft': 'auto'}
                                            )
                                        ],
                                        direction="horizontal",
                                        style={'width': '100%', 'alignItems': 'center'}
                                    )
                                )
                            ],
                            align="middle"
                        ),
                        style={'padding': '12px 0'}
                    )
                ],
                style={'marginTop': '16px'}
            )
        ]
    )


def _render_health_history_tab():
    """渲染健康史Tab内容"""
    return html.Div(
        [
            # 家族史卡片
            NoTitleCard(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                flex="auto",
                                children=fac.AntdText("家族史", strong=True, style={'fontSize': '16px'})
                            ),
                            fac.AntdCol(
                                children=fac.AntdButton("编辑", type="link", size="small")
                            )
                        ],
                        align="middle"
                    ),
                    fac.AntdDivider(style={'margin': '12px 0'}),
                    fac.AntdSpace(
                        [
                            fac.AntdTag("高血压", color="red"),
                            fac.AntdTag("糖尿病", color="orange"),
                            fac.AntdTag("心脏病", color="purple")
                        ],
                        style={'marginBottom': '8px'}
                    ),
                    fac.AntdText("父亲患有高血压和糖尿病，母亲有心脏病病史", type="secondary")
                ],
                style={'marginBottom': '16px'}
            ),
            # 个人史卡片
            NoTitleCard(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                flex="auto",
                                children=fac.AntdText("个人史", strong=True, style={'fontSize': '16px'})
                            ),
                            fac.AntdCol(
                                children=fac.AntdButton("编辑", type="link", size="small")
                            )
                        ],
                        align="middle"
                    ),
                    fac.AntdDivider(style={'margin': '12px 0'}),
                    fac.AntdSpace(
                        [
                            fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-file-text", style={'color': '#1890ff'}),
                                    fac.AntdText("饮酒情况：", strong=True),
                                    fac.AntdText("偶尔饮酒，每周1-2次")
                                ],
                                style={'width': '100%', 'marginBottom': '8px'}
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-file-text", style={'color': '#1890ff'}),
                                    fac.AntdText("吸烟情况：", strong=True),
                                    fac.AntdText("已戒烟3年")
                                ],
                                style={'width': '100%', 'marginBottom': '8px'}
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdIcon(icon="antd-file-text", style={'color': '#1890ff'}),
                                    fac.AntdText("过敏史：", strong=True),
                                    fac.AntdText("青霉素过敏")
                                ],
                                style={'width': '100%'}
                            )
                        ],
                        direction="vertical",
                        style={'width': '100%'}
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 既往病史卡片
            NoTitleCard(
                [
                    fac.AntdRow(
                        [
                            fac.AntdCol(
                                flex="auto",
                                children=fac.AntdText("既往病史", strong=True, style={'fontSize': '16px'})
                            ),
                            fac.AntdCol(
                                children=fac.AntdButton("编辑", type="link", size="small")
                            )
                        ],
                        align="middle"
                    ),
                    fac.AntdDivider(style={'margin': '12px 0'}),
                    fac.AntdTimeline(
                        items=[
                            {
                                "label": fac.AntdText("2023年6月", strong=True),
                                "content": fac.AntdText("急性胃炎，已治愈", type="secondary")
                            },
                            {
                                "label": fac.AntdText("2022年3月", strong=True),
                                "content": fac.AntdText("阑尾炎手术", type="secondary")
                            },
                            {
                                "label": fac.AntdText("2021年1月", strong=True),
                                "content": fac.AntdText("感冒发烧", type="secondary")
                            }
                        ],
                        style={'marginTop': '12px'}
                    )
                ]
            )
        ]
    )


def _render_health_check_tab():
    """渲染健康自测Tab内容"""
    return html.Div(
        [
            # 自测记录列表
            html.Div(
                [
                    NoTitleCard(
                        [
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        flex="auto",
                                        children=fac.AntdSpace(
                                            [
                                                fac.AntdText("血压自测", strong=True, style={'fontSize': '16px'}),
                                                fac.AntdDivider(direction="vertical"),
                                                fac.AntdText("125/80 mmHg", style={'fontSize': '18px', 'color': '#1890ff'}),
                                                fac.AntdTag("正常", color="green"),
                                                fac.AntdText("2024-03-20 08:30", type="secondary", style={'marginLeft': 'auto'})
                                            ],
                                            direction="horizontal",
                                            style={'width': '100%', 'alignItems': 'center'}
                                        )
                                    ),
                                    fac.AntdCol(
                                        flex="none",
                                        children=fac.AntdButton("查看详情", type="link", size="small")
                                    )
                                ],
                                align="middle"
                            )
                        ],
                        style={'marginBottom': '12px'}
                    ),
                    NoTitleCard(
                        [
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        flex="auto",
                                        children=fac.AntdSpace(
                                            [
                                                fac.AntdText("血糖自测", strong=True, style={'fontSize': '16px'}),
                                                fac.AntdDivider(direction="vertical"),
                                                fac.AntdText("5.8 mmol/L", style={'fontSize': '18px', 'color': '#1890ff'}),
                                                fac.AntdTag("正常", color="green"),
                                                fac.AntdText("2024-03-20 07:00", type="secondary", style={'marginLeft': 'auto'})
                                            ],
                                            direction="horizontal",
                                            style={'width': '100%', 'alignItems': 'center'}
                                        )
                                    ),
                                    fac.AntdCol(
                                        flex="none",
                                        children=fac.AntdButton("查看详情", type="link", size="small")
                                    )
                                ],
                                align="middle"
                            )
                        ],
                        style={'marginBottom': '12px'}
                    ),
                    NoTitleCard(
                        [
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        flex="auto",
                                        children=fac.AntdSpace(
                                            [
                                                fac.AntdText("体重测量", strong=True, style={'fontSize': '16px'}),
                                                fac.AntdDivider(direction="vertical"),
                                                fac.AntdText("72.5 kg", style={'fontSize': '18px', 'color': '#1890ff'}),
                                                fac.AntdTag("正常", color="blue"),
                                                fac.AntdText("2024-03-19 19:00", type="secondary", style={'marginLeft': 'auto'})
                                            ],
                                            direction="horizontal",
                                            style={'width': '100%', 'alignItems': 'center'}
                                        )
                                    ),
                                    fac.AntdCol(
                                        flex="none",
                                        children=fac.AntdButton("查看详情", type="link", size="small")
                                    )
                                ],
                                align="middle"
                            )
                        ],
                        style={'marginBottom': '12px'}
                    ),
                    NoTitleCard(
                        [
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        flex="auto",
                                        children=fac.AntdSpace(
                                            [
                                                fac.AntdText("体温测量", strong=True, style={'fontSize': '16px'}),
                                                fac.AntdDivider(direction="vertical"),
                                                fac.AntdText("36.5°C", style={'fontSize': '18px', 'color': '#1890ff'}),
                                                fac.AntdTag("正常", color="green"),
                                                fac.AntdText("2024-03-19 18:00", type="secondary", style={'marginLeft': 'auto'})
                                            ],
                                            direction="horizontal",
                                            style={'width': '100%', 'alignItems': 'center'}
                                        )
                                    ),
                                    fac.AntdCol(
                                        flex="none",
                                        children=fac.AntdButton("查看详情", type="link", size="small")
                                    )
                                ],
                                align="middle"
                            )
                        ],
                        style={'marginBottom': '12px'}
                    ),
                    NoTitleCard(
                        [
                            fac.AntdRow(
                                [
                                    fac.AntdCol(
                                        flex="auto",
                                        children=fac.AntdSpace(
                                            [
                                                fac.AntdText("心率测量", strong=True, style={'fontSize': '16px'}),
                                                fac.AntdDivider(direction="vertical"),
                                                fac.AntdText("78 bpm", style={'fontSize': '18px', 'color': '#1890ff'}),
                                                fac.AntdTag("正常", color="green"),
                                                fac.AntdText("2024-03-19 18:00", type="secondary", style={'marginLeft': 'auto'})
                                            ],
                                            direction="horizontal",
                                            style={'width': '100%', 'alignItems': 'center'}
                                        )
                                    ),
                                    fac.AntdCol(
                                        flex="none",
                                        children=fac.AntdButton("查看详情", type="link", size="small")
                                    )
                                ],
                                align="middle"
                            )
                        ],
                        style={'marginBottom': '12px'}
                    )
                ],
                style={'marginTop': '16px'}
            ),
            # 添加自测按钮
            fac.AntdButton(
                "添加自测记录",
                type="primary",
                block=True,
                icon=fac.AntdIcon(icon="antd-plus"),
                style={'marginTop': '16px'}
            )
        ]
    )


def _render_medication_record_tab():
    """渲染药物记录Tab内容"""
    return html.Div(
        [
            # 当前用药
            NoTitleCard(
                [
                    fac.AntdText("当前用药", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    html.Div(
                        [
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("阿司匹林肠溶片", strong=True, style={'fontSize': '15px'}),
                                        fac.AntdTag("进行中", color="blue"),
                                        fac.AntdText("剂量：100mg", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("每日1次，饭后服用", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("长期服用", type="secondary"),
                                        fac.AntdSpace(
                                            [
                                                fac.AntdButton("详情", type="link", size="small"),
                                                fac.AntdButton("暂停", type="link", size="small", danger=True)
                                            ],
                                            style={'marginLeft': 'auto'}
                                        )
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("氨氯地平片", strong=True, style={'fontSize': '15px'}),
                                        fac.AntdTag("进行中", color="blue"),
                                        fac.AntdText("剂量：5mg", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("每日1次，早饭后服用", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("长期服用", type="secondary"),
                                        fac.AntdSpace(
                                            [
                                                fac.AntdButton("详情", type="link", size="small"),
                                                fac.AntdButton("暂停", type="link", size="small", danger=True)
                                            ],
                                            style={'marginLeft': 'auto'}
                                        )
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            )
                        ]
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 用药历史
            NoTitleCard(
                [
                    fac.AntdText("用药历史", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    fac.AntdTimeline(
                        items=[
                            {
                                "label": fac.AntdText("2024年2月", strong=True),
                                "content": html.Div([
                                    fac.AntdText("感冒灵颗粒 - 已停用", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("服用时间：2024-02-10 至 2024-02-17", type="secondary")
                                ])
                            },
                            {
                                "label": fac.AntdText("2023年12月", strong=True),
                                "content": html.Div([
                                    fac.AntdText("头孢克肟胶囊 - 已停用", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("服用时间：2023-12-05 至 2023-12-12", type="secondary")
                                ])
                            },
                            {
                                "label": fac.AntdText("2023年9月", strong=True),
                                "content": html.Div([
                                    fac.AntdText("布洛芬缓释胶囊 - 已停用", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("服用时间：2023-09-15 至 2023-09-22", type="secondary")
                                ])
                            }
                        ],
                        style={'marginTop': '12px'}
                    )
                ]
            ),
            # 添加用药按钮
            fac.AntdButton(
                "添加用药记录",
                type="primary",
                block=True,
                icon=fac.AntdIcon(icon="antd-plus"),
                style={'marginTop': '16px'}
            )
        ]
    )


def _render_exercise_health_tab():
    """渲染运动健康Tab内容"""
    return html.Div(
        [
            # 今日运动数据卡片
            NoTitleCard(
                [
                    fac.AntdText("今日运动", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    html.Div(
                        [
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("步数", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("8,234", strong=True, style={'fontSize': '24px', 'color': '#1890ff', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("距离", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("5.8 km", strong=True, style={'fontSize': '24px', 'color': '#52c41a', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("卡路里", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("456", strong=True, style={'fontSize': '24px', 'color': '#faad14', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("运动时长", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("45分钟", strong=True, style={'fontSize': '24px', 'color': '#722ed1', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            )
                        ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-around',
                            'alignItems': 'center',
                            'marginTop': '12px',
                            'width': '100%'
                        }
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 运动记录列表
            NoTitleCard(
                [
                    fac.AntdText("运动记录", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    html.Div(
                        [
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag("慢跑", color="blue"),
                                        fac.AntdText("时长：30分钟", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("距离：4.5 km", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("消耗：280 卡路里", type="secondary"),
                                        fac.AntdText("2024-03-19 07:00", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag("快走", color="blue"),
                                        fac.AntdText("时长：20分钟", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("距离：2.1 km", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("消耗：120 卡路里", type="secondary"),
                                        fac.AntdText("2024-03-19 18:30", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag("游泳", color="blue"),
                                        fac.AntdText("时长：45分钟", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("距离：800米", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("消耗：350 卡路里", type="secondary"),
                                        fac.AntdText("2024-03-18 19:00", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdTag("骑行", color="blue"),
                                        fac.AntdText("时长：60分钟", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("距离：15 km", type="secondary"),
                                        fac.AntdDivider(direction="vertical"),
                                        fac.AntdText("消耗：420 卡路里", type="secondary"),
                                        fac.AntdText("2024-03-17 08:00", type="secondary", style={'marginLeft': 'auto'})
                                    ],
                                    direction="horizontal",
                                    style={'width': '100%', 'alignItems': 'center', 'flexWrap': 'wrap'}
                                ),
                                style={'padding': '12px 0', 'borderBottom': '1px solid #f0f0f0'}
                            )
                        ]
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 添加运动记录按钮
            fac.AntdButton(
                "添加运动记录",
                type="primary",
                block=True,
                icon=fac.AntdIcon(icon="antd-plus"),
                style={'marginTop': '16px'}
            )
        ]
    )


def _render_diet_health_tab():
    """渲染饮食健康Tab内容"""
    return html.Div(
        [
            # 今日饮食统计
            NoTitleCard(
                [
                    fac.AntdText("今日饮食", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    html.Div(
                        [
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("摄入卡路里", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("1,856", strong=True, style={'fontSize': '28px', 'color': '#1890ff', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("目标卡路里", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("2,000", strong=True, style={'fontSize': '28px', 'color': '#52c41a', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            ),
                            html.Div(
                                fac.AntdSpace(
                                    [
                                        fac.AntdText("剩余", type="secondary", style={'fontSize': '14px'}),
                                        fac.AntdText("144", strong=True, style={'fontSize': '28px', 'color': '#faad14', 'whiteSpace': 'nowrap'})
                                    ],
                                    direction="vertical",
                                    style={'textAlign': 'center'}
                                ),
                                style={'flex': '1', 'minWidth': '0'}
                            )
                        ],
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-around',
                            'alignItems': 'center',
                            'marginTop': '12px',
                            'width': '100%'
                        }
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 饮食记录
            NoTitleCard(
                [
                    fac.AntdText("饮食记录", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    fac.AntdTimeline(
                        items=[
                            {
                                "icon": fac.AntdIcon(icon="antd-coffee", style={'color': '#1890ff'}),
                                "label": fac.AntdText("早餐", strong=True),
                                "content": html.Div([
                                    fac.AntdText("小米粥、鸡蛋、咸菜", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("约 450 卡路里 | 2024-03-20 08:00", type="secondary")
                                ])
                            },
                            {
                                "icon": fac.AntdIcon(icon="antd-apple", style={'color': '#52c41a'}),
                                "label": fac.AntdText("午餐", strong=True),
                                "content": html.Div([
                                    fac.AntdText("米饭、红烧肉、青菜、紫菜蛋花汤", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("约 680 卡路里 | 2024-03-20 12:30", type="secondary")
                                ])
                            },
                            {
                                "icon": fac.AntdIcon(icon="antd-restaurant", style={'color': '#faad14'}),
                                "label": fac.AntdText("晚餐", strong=True),
                                "content": html.Div([
                                    fac.AntdText("面条、番茄鸡蛋、凉拌黄瓜", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("约 520 卡路里 | 2024-03-20 18:00", type="secondary")
                                ])
                            },
                            {
                                "icon": fac.AntdIcon(icon="antd-gift", style={'color': '#722ed1'}),
                                "label": fac.AntdText("加餐", strong=True),
                                "content": html.Div([
                                    fac.AntdText("苹果、酸奶", type="secondary"),
                                    html.Br(),
                                    fac.AntdText("约 206 卡路里 | 2024-03-20 15:00", type="secondary")
                                ])
                            }
                        ],
                        style={'marginTop': '12px'}
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 营养分析
            NoTitleCard(
                [
                    fac.AntdText("营养分析", strong=True, style={'fontSize': '16px', 'marginBottom': '12px'}),
                    fac.AntdDivider(style={'margin': '8px 0'}),
                    fac.AntdSpace(
                        [
                            fac.AntdSpace(
                                [
                                    fac.AntdText("蛋白质", style={'width': '80px'}),
                                    fac.AntdProgress(percent=75, status="active", style={'flex': 1}),
                                    fac.AntdText("75%", type="secondary", style={'width': '50px', 'textAlign': 'right'})
                                ],
                                direction="horizontal",
                                style={'width': '100%', 'alignItems': 'center'}
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdText("碳水化合物", style={'width': '80px'}),
                                    fac.AntdProgress(percent=65, status="active", style={'flex': 1}),
                                    fac.AntdText("65%", type="secondary", style={'width': '50px', 'textAlign': 'right'})
                                ],
                                direction="horizontal",
                                style={'width': '100%', 'alignItems': 'center'}
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdText("脂肪", style={'width': '80px'}),
                                    fac.AntdProgress(percent=45, status="active", style={'flex': 1}),
                                    fac.AntdText("45%", type="secondary", style={'width': '50px', 'textAlign': 'right'})
                                ],
                                direction="horizontal",
                                style={'width': '100%', 'alignItems': 'center'}
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdText("维生素", style={'width': '80px'}),
                                    fac.AntdProgress(percent=80, status="active", style={'flex': 1}),
                                    fac.AntdText("80%", type="secondary", style={'width': '50px', 'textAlign': 'right'})
                                ],
                                direction="horizontal",
                                style={'width': '100%', 'alignItems': 'center'}
                            )
                        ],
                        direction="vertical",
                        style={'width': '100%', 'marginTop': '12px'}
                    )
                ],
                style={'marginBottom': '16px'}
            ),
            # 添加饮食记录按钮
            fac.AntdButton(
                "添加饮食记录",
                type="primary",
                block=True,
                icon=fac.AntdIcon(icon="antd-plus"),
                style={'marginTop': '16px'}
            )
        ]
    )


# 在文件末尾添加以下代码
app.clientside_callback(
    ClientsideFunction(
        namespace="clientside_basic",
        function_name="handleResponsiveDrawerWidth"
    ),
    Output("health-record-drawer", "width"),
    Input("health-record-drawer", "visible"),
    prevent_initial_call=False
)