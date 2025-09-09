import dash
from dash import ctx, Input, Output, State, callback
import feffery_antd_components as fac
import json

# 此回调假设输入框及按钮已存在页面布局中，回调示意：输入后点击发送按钮，将输入内容存入Store，并清空输入框
def register_chat_input_callbacks(app):
    # 新增：话题提示栏点击同步到输入框内容回调
    topic_inputs = [Input(f'chat-topic-{i}', 'nClicks') for i in range(4)]
    @callback(
        Output('ai-chat-x-input', 'value'),
        topic_inputs,
        State('ai-chat-x-input', 'value'),
        prevent_initial_call=True
    )
    def topic_click_to_input(*args):
        # args = [nClicks_0, nClicks_1, nClicks_2, nClicks_3, input_value]
        topics = ["如何提高工作效率", "数据分析技巧", "代码优化建议", "项目管理方法"]
        input_value = args[-1]
        for i, n in enumerate(args[:-1]):
            if ctx.triggered_id == f'chat-topic-{i}' and n:
                return topics[i]
        return dash.no_update

# 若全局注册，需在app.py或server.py中import并调用 register_chat_input_callbacks(app) 即可