# 语音实时对话文本显示方案（修订版）

## 问题分析

### 当前设计
- **录音聊天（voice_recording）**：收到 `transcription_result` → 更新 `voice-transcription-store-server` → 触发 `handle_chat_interactions` → 添加到 `messages` → 触发 SSE → 显示文本和音频 → **保存到数据库**
- **语音实时对话（voice_call）**：发送音频流 → 收到 `audio_stream` → 直接播放音频（**不显示文本，不保存到数据库**）

### 核心问题
如果将语音实时对话的转录文本直接写入 `messages` store，会：
1. 触发 `handle_chat_interactions` 回调
2. 启动 SSE 流程
3. 干扰语音实时对话的音频流处理
4. 造成流程混乱
5. **自动保存到数据库，可能导致不需要的消息被保存**

### 新增考虑点

1. **消息保存逻辑**：
   - 当前文本聊天和录音聊天都会保存到 `Conversations.conv_memory.messages`
   - 语音实时对话是否需要保存？何时保存？
   - 如果保存，是否应该标记为语音实时对话类型？

2. **显示方式**：
   - 是否流式显示？**建议：非流式显示**（整句显示，避免闪烁和性能问题）

3. **UI集成位置**：
   - 独立显示组件放在哪里？
   - 如何不影响现有聊天历史显示？

## 解决方案

### 架构设计

```
语音实时对话流程（独立，不影响文本聊天）：
┌─────────────────┐
│ 音频流发送      │
│ (voice_call)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 后端处理        │
│ - 转写文本      │
│ - 生成回复      │
│ - 生成音频      │
└────────┬────────┘
         │
         ├─── audio_stream ────┐
         │                      ▼
         │              ┌──────────────┐
         │              │ 播放音频     │
         │              └──────────────┘
         │
         └─── transcription_result (可选) ───┐
                                             ▼
                                      ┌──────────────┐
                                      │ 独立显示     │
                                      │ (不触发SSE)  │
                                      └──────────────┘
```

### 核心原则

1. **完全隔离**：语音实时对话的文本显示使用独立的存储，不触发任何文本聊天逻辑
2. **场景区分**：通过 `scenario` 字段区分转录来源
3. **可配置**：后端可配置是否发送 transcription_result，前端可配置是否显示和保存
4. **性能优先**：文本更新使用累积更新机制，非流式显示，不影响音频流处理
5. **保存策略**：可选保存到数据库，标记为语音实时对话类型，会话结束时统一保存
6. **UI集成**：独立显示组件，不干扰主聊天历史显示

## 实现方案

### 1. 配置项（VoiceConfig）

```python
# configs/voice_config.py
class VoiceConfig:
    # ... 现有配置 ...
    
    # 语音实时对话文本显示配置
    VOICE_CALL_SHOW_TRANSCRIPTION = True  # 是否显示转录文本（前端配置）
    VOICE_CALL_SAVE_TO_DATABASE = False  # 是否保存到数据库（默认不保存，避免干扰）
    VOICE_CALL_AUTO_SAVE_ON_END = True  # 对话结束时是否自动保存（如果VOICE_CALL_SAVE_TO_DATABASE=True）
    VOICE_CALL_MAX_DISPLAY_MESSAGES = 50  # 最大显示消息数
    VOICE_CALL_TRANSCRIPTION_DEBOUNCE = 500  # 文本更新防抖时间（毫秒）
    VOICE_CALL_STREAMING_DISPLAY = False  # 是否流式显示（建议False，整句显示）
```

### 2. 新增独立存储组件

```python
# views/core_pages/chat.py
voice_call_transcription_display = dcc.Store(
    id='voice-call-transcription-display',
    data={
        'messages': [],  # 格式: [{'role': 'user'|'assistant', 'text': str, 'timestamp': float, 'message_id': str}]
        'is_active': False,  # 是否在语音实时对话中
        'session_id': None,  # 当前会话ID
        'call_start_time': None,  # 对话开始时间
        'max_messages': 50,  # 最大消息数（限制内存使用）
        'created_at': None  # Store创建时间
    }
)
```

### 3. 后端修改（yychat项目）

#### 3.1 transcription_result 消息格式增强

```python
# yychat/core/realtime_handler.py 或相关文件

# 发送转录结果时添加 scenario 字段
await websocket_manager.send_message(client_id, {
    "type": "transcription_result",
    "text": transcribed_text,
    "timestamp": time.time(),
    "client_id": client_id,
    "scenario": "voice_call",  # 新增：标识场景类型
    "message_id": message_id,  # 可选：关联的message_id
})
```

#### 3.2 配置项控制

```python
# yychat/config/realtime_config.py
class RealtimeConfig:
    # ... 现有配置 ...
    
    # 是否在语音实时对话中发送transcription_result
    VOICE_CALL_SEND_TRANSCRIPTION = True
    
    # 是否在发送transcription_result时包含AI回复文本
    VOICE_CALL_INCLUDE_ASSISTANT_TEXT = True  # 可选：同时显示AI的文本回复
```

### 4. 前端修改

#### 4.1 独立的文本显示组件 - UI集成方案

**方案A：悬浮面板（推荐）**
在聊天历史区域上方显示，悬浮在聊天内容上方，不影响主聊天历史滚动。

```python
# views/core_pages/chat.py
# 在 _create_content_area() 中，chat_history 之前添加
voice_call_text_display = html.Div(
    id='voice-call-text-display',
    style={
        'display': 'none',  # 默认隐藏，仅在语音实时对话时显示
        'position': 'absolute',  # 绝对定位
        'top': '60px',  # 头部下方
        'left': '24px',
        'right': '24px',
        'zIndex': 100,  # 确保在聊天历史上方
        'maxHeight': '200px',
        'overflowY': 'auto',
        'padding': '12px 16px',
        'backgroundColor': '#fff',
        'borderRadius': '8px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.15)',
        'border': '1px solid #e8e8e8'
    },
    children=[
        fac.AntdRow(
            [
                fac.AntdCol(
                    fac.AntdText('语音实时对话', strong=True, style={'fontSize': '14px'}),
                    flex='auto'
                ),
                fac.AntdCol(
                    fac.AntdButton(
                        icon=fac.AntdIcon(icon='antd-close'),
                        type='text',
                        size='small',
                        id='voice-call-text-close-btn'
                    ),
                    flex='none'
                )
            ],
            align='middle'
        ),
        html.Div(
            id='voice-call-text-content',
            style={
                'marginTop': '12px',
                'maxHeight': '150px',
                'overflowY': 'auto'
            },
            children=[]
        )
    ]
)

# 修改 chat_history，添加相对定位，使悬浮面板正确定位
chat_history = fuc.FefferyDiv(
    id="ai-chat-x-history",
    children=[
        voice_call_text_display,  # 添加悬浮面板
        html.Div(
            id="ai-chat-x-history-content",
            children=AiChatMessageHistory(messages=None),
            **{"data-dummy": {}}
        )
    ],
    scrollbar='simple',
    style=style(
        position='relative',  # 添加相对定位
        height="calc(100vh - 240px)",
        maxHeight="calc(100vh - 240px)",
        overflowY="auto",
        backgroundColor="#fafafa",
        minWidth=0
    )
)
```

**方案B：顶部固定区域**
在聊天头部下方显示，固定位置，始终可见。

```python
# views/core_pages/chat.py
# 在 chat_header 和 chat_history 之间添加
voice_call_text_display = html.Div(
    id='voice-call-text-display',
    style={
        'display': 'none',
        'maxHeight': '150px',
        'overflowY': 'auto',
        'padding': '8px 16px',
        'backgroundColor': '#f9f9f9',
        'borderBottom': '1px solid #e8e8e8',
        'flexShrink': 0  # 不被压缩
    },
    children=[
        fac.AntdText('语音实时对话', strong=True, style={'fontSize': '12px', 'color': '#666'}),
        html.Div(
            id='voice-call-text-content',
            style={'marginTop': '8px'},
            children=[]
        )
    ]
)

# 修改 _create_content_area()，在 chat_header 和 chat_history 之间插入
return fuc.FefferyDiv(
    [chat_header,
     voice_call_text_display,  # 添加文本显示区域
     SSE(...),
     chat_history],
    ...
)
```

**方案C：底部固定区域（类似输入提示）**
在输入区域上方显示，类似输入提示。

```python
# views/core_pages/chat.py
# 在 _create_input_content() 中添加
voice_call_text_display = html.Div(
    id='voice-call-text-display',
    style={
        'display': 'none',
        'maxHeight': '150px',
        'overflowY': 'auto',
        'padding': '8px 16px',
        'backgroundColor': '#f9f9f9',
        'borderTop': '1px solid #e8e8e8',
        'borderBottom': '1px solid #e8e8e8',
        'flexShrink': 0
    },
    children=[
        fac.AntdText('语音实时对话', strong=True, style={'fontSize': '12px', 'color': '#666'}),
        html.Div(
            id='voice-call-text-content',
            style={'marginTop': '8px'},
            children=[]
        )
    ]
)

# 在 _create_input_content() 中
def _create_input_content():
    return html.Div([
        voice_call_text_display,  # 添加文本显示区域
        html.Div(
            id='ai-chat-x-input-container',
            children=render_chat_input_area()
        )
    ])
```

**推荐方案：方案A（悬浮面板）**
- ✅ 不占用固定空间，不影响聊天历史显示
- ✅ 视觉上清晰区分语音实时对话文本和主聊天历史
- ✅ 可以最小化或关闭
- ✅ 不会影响输入区域

#### 4.2 前端处理逻辑（voice_websocket_manager.js）

```javascript
// assets/js/voice_websocket_manager.js

// 处理 transcription_result 时区分场景
handleMessage(data) {
    // ... 现有代码 ...
    
    if (message.type === 'transcription_result') {
        const scenario = message.scenario || 'voice_recording';  // 默认为录音聊天
        
        if (scenario === 'voice_call') {
            // 语音实时对话：只更新显示，不触发文本聊天逻辑
            this.handleVoiceCallTranscription(message);
        } else {
            // 录音聊天：使用现有逻辑，更新 voice-transcription-store-server
            // 现有代码保持不变
            this.handleVoiceRecordingTranscription(message);
        }
    }
}

// 新增：处理语音实时对话的转录结果（非流式显示，整句显示）
handleVoiceCallTranscription(message) {
    try {
        const text = message.text;
        const messageId = message.message_id || null;
        const timestamp = message.timestamp || Date.now() / 1000;
        
        // 累积待更新消息（避免数据丢失）
        if (!this.pendingVoiceCallMessages) {
            this.pendingVoiceCallMessages = [];
        }
        
        // 添加用户消息到待更新队列
        this.pendingVoiceCallMessages.push({
            role: 'user',
            text: text,
            timestamp: timestamp,
            message_id: messageId || `voice-call-user-${Date.now()}`
        });
        
        // 如果后端同时发送了AI回复文本（非流式，完整文本）
        if (message.assistant_text) {
            this.pendingVoiceCallMessages.push({
                role: 'assistant',
                text: message.assistant_text,  // 完整文本，非流式
                timestamp: timestamp + 0.001,
                message_id: message.assistant_message_id || `voice-call-assistant-${Date.now()}`
            });
        }
        
        // 使用累积更新机制（防抖批量处理）
        this.debounceUpdateVoiceCallDisplay();
    } catch (error) {
        console.error('处理语音实时对话转录失败:', error);
    }
}

// 累积更新机制（改进版）
debounceUpdateVoiceCallDisplay() {
    if (this.voiceCallDisplayUpdateTimer) {
        clearTimeout(this.voiceCallDisplayUpdateTimer);
    }
    
    this.voiceCallDisplayUpdateTimer = setTimeout(() => {
        // 批量处理所有待更新消息
        if (!this.pendingVoiceCallMessages || this.pendingVoiceCallMessages.length === 0) {
            return;
        }
        
        // 获取当前显示数据
        const currentDisplay = this.voiceCallTranscriptionDisplay || {
            messages: [],
            is_active: true,
            session_id: this.sessionId,
            max_messages: 50,
            created_at: Date.now()
        };
        
        // 批量添加待更新消息
        while (this.pendingVoiceCallMessages.length > 0) {
            const msg = this.pendingVoiceCallMessages.shift();
            currentDisplay.messages.push(msg);
        }
        
        // 限制消息数量（保持最新的50条）
        if (currentDisplay.messages.length > currentDisplay.max_messages) {
            currentDisplay.messages = currentDisplay.messages.slice(-currentDisplay.max_messages);
        }
        
        // 保存到实例变量
        this.voiceCallTranscriptionDisplay = currentDisplay;
        
        // 更新Store（不触发任何Dash回调）
        if (window.dash_clientside && window.dash_clientside.set_props) {
            window.dash_clientside.set_props('voice-call-transcription-display', {
                data: currentDisplay
            });
        }
        
        // 更新UI显示（非流式，整句显示）
        this.updateVoiceCallTextDisplay(currentDisplay);
    }, 500);  // 500ms防抖
}

// 更新UI显示（非流式，整句显示）
updateVoiceCallTextDisplay(displayData) {
    const displayElement = document.getElementById('voice-call-text-content');
    if (!displayElement) return;
    
    if (!displayData || !displayData.messages || displayData.messages.length === 0) {
        displayElement.innerHTML = '<div style="text-align: center; color: #999; font-size: 12px; padding: 20px;">暂无对话记录</div>';
        return;
    }
    
    // 只显示最近的10条消息，避免DOM过大（悬浮面板限制）
    const recentMessages = displayData.messages.slice(-10);
    
    // 非流式显示：整句渲染，不逐字显示
    displayElement.innerHTML = recentMessages.map(msg => {
        const isUser = msg.role === 'user';
        const timeStr = new Date(msg.timestamp * 1000).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        return `
            <div style="margin-bottom: 8px; padding: 8px 12px; border-radius: 6px; 
                        background-color: ${isUser ? '#e6f7ff' : '#f6ffed'}; 
                        border-left: 3px solid ${isUser ? '#1890ff' : '#52c41a'};">
                <div style="font-size: 11px; color: #999; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <span>${isUser ? '👤 用户' : '🤖 AI'}</span>
                    <span>${timeStr}</span>
                </div>
                <div style="font-size: 14px; line-height: 1.6; color: #333; word-wrap: break-word;">
                    ${this.escapeHtml(msg.text || '')}
                </div>
            </div>
        `;
    }).join('');
    
    // 滚动到底部
    displayElement.scrollTop = displayElement.scrollHeight;
}

// HTML转义（防止XSS）
escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 语音实时对话开始时
startVoiceCall() {
    // ... 现有代码 ...
    
    // 初始化文本显示
    if (window.dash_clientside && window.dash_clientside.set_props) {
        window.dash_clientside.set_props('voice-call-transcription-display', {
            data: {
                messages: [],
                is_active: true,
                session_id: this.sessionId
            }
        });
    }
    
    // 显示文本显示区域（如果有）
    const displayElement = document.getElementById('voice-call-text-display');
    if (displayElement) {
        displayElement.style.display = 'block';
    }
}

// 语音实时对话结束时
stopVoiceCall() {
    // ... 现有代码 ...
    
    // 隐藏文本显示区域
    const displayElement = document.getElementById('voice-call-text-display');
    if (displayElement) {
        displayElement.style.display = 'none';
    }
    
    // 清理显示数据（可选：保留历史）
    // this.voiceCallTranscriptionDisplay = null;
}
```

### 5. 消息保存逻辑

#### 5.1 保存策略设计

**问题**：语音实时对话的消息是否需要保存到数据库？

**方案**：
1. **默认不保存**：避免干扰正常聊天流程，避免自动触发保存
2. **可选保存**：通过配置项 `VOICE_CALL_SAVE_TO_DATABASE` 控制
3. **延迟保存**：在语音实时对话结束时统一保存（如果启用保存）
4. **标记区分**：保存时添加 `source: 'voice_call'` 标记，与文本聊天区分

#### 5.2 保存实现

```python
# callbacks/voice_call_display_c.py (新建文件)

@app.callback(
    Output('voice-call-save-trigger', 'data'),  # 虚拟输出，用于触发保存
    Input('voice-call-status', 'data'),  # 监听语音实时对话状态
    State('voice-call-transcription-display', 'data'),
    State('ai-chat-x-current-session-id', 'data'),
    prevent_initial_call=True
)
def save_voice_call_messages(voice_call_status, display_data, current_session_id):
    """语音实时对话结束时，可选保存消息到数据库"""
    
    from configs.voice_config import VoiceConfig
    from models.conversations import Conversations
    
    # 检查是否启用保存
    if not VoiceConfig.VOICE_CALL_SAVE_TO_DATABASE:
        return dash.no_update
    
    # 检查是否对话已结束（从 active 变为 inactive）
    if not display_data or not display_data.get('messages'):
        return dash.no_update
    
    # 检查状态变化（简化：如果 messages 不为空且对话已结束）
    is_active = display_data.get('is_active', False)
    if is_active:
        return dash.no_update  # 对话进行中，不保存
    
    # 对话已结束，保存消息
    try:
        messages = display_data.get('messages', [])
        if not messages or not current_session_id:
            return dash.no_update
        
        conv = Conversations.get_conversation_by_conv_id(current_session_id)
        if conv:
            existing_messages = conv.conv_memory.get('messages', []) if conv.conv_memory else []
            
            # 添加语音实时对话消息，标记来源
            for msg in messages:
                existing_messages.append({
                    'role': msg.get('role'),
                    'content': msg.get('text'),
                    'timestamp': datetime.fromtimestamp(msg.get('timestamp', time.time())).strftime('%Y-%m-%d %H:%M:%S'),
                    'id': msg.get('message_id'),
                    'source': 'voice_call'  # 标记为语音实时对话
                })
            
            Conversations.update_conversation_by_conv_id(
                current_session_id,
                conv_memory={'messages': existing_messages}
            )
            log.info(f"✅ 语音实时对话消息已保存到数据库: {current_session_id}, 消息数: {len(messages)}")
    except Exception as e:
        log.error(f"保存语音实时对话消息失败: {e}")
    
    return dash.no_update
```

**更简单的方案（前端控制）**：
在 `voice_websocket_manager.js` 的 `stopVoiceCall` 方法中，如果启用保存，调用后端API保存：

```javascript
// assets/js/voice_websocket_manager.js
async stopVoiceCall() {
    // ... 现有代码 ...
    
    // 可选保存消息到数据库
    if (window.voiceConfig && window.voiceConfig.VOICE_CALL_SAVE_TO_DATABASE) {
        await this.saveVoiceCallMessages();
    }
}

async saveVoiceCallMessages() {
    const displayData = this.voiceCallTranscriptionDisplay;
    if (!displayData || !displayData.messages || displayData.messages.length === 0) {
        return;
    }
    
    try {
        // 调用后端API保存（需要新增API端点）
        const response = await fetch('/api/voice-call/save-messages', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: displayData.session_id,
                messages: displayData.messages,
                source: 'voice_call'
            })
        });
        
        if (response.ok) {
            window.controlledLog?.log('✅ 语音实时对话消息已保存到数据库');
        }
    } catch (error) {
        console.error('保存语音实时对话消息失败:', error);
    }
}
```

#### 5.3 消息格式标记

保存到数据库时，添加 `source` 字段区分：
```python
{
    'role': 'user',
    'content': '用户说的话',
    'timestamp': '2025-11-01 21:45:13',
    'id': 'voice-call-user-xxx',
    'source': 'voice_call'  # 新增：标记来源
}
```

### 6. 保持现有功能不变

#### 6.1 录音聊天的处理保持不变

```python
# callbacks/core_pages_c/chat_input_area_c.py
# handle_chat_interactions 函数中的处理逻辑完全不变

# 只处理 voice_recording 场景的 transcription_result
# voice_call 场景的 transcription_result 不会触发这里
```

#### 6.2 前端区分逻辑（必须修改）

```javascript
// assets/js/voice_recorder_enhanced.js
handleTranscriptionResult(data) {
    // 🔧 关键修复：检查场景类型
    const scenario = data.scenario || 'voice_recording';
    
    if (scenario === 'voice_call') {
        // 语音实时对话：不处理，交给 voice_websocket_manager.js
        window.controlledLog?.log('收到语音实时对话转录结果，跳过录音聊天处理');
        return;
    }
    
    // 录音聊天：使用现有逻辑
    // ... 现有代码保持不变 ...
}
```

#### 6.3 voice_websocket_manager.js 注册处理器（必须修改）

```javascript
// assets/js/voice_websocket_manager.js
registerMessageHandlers() {
    // ... 现有代码 ...
    
    // 🔧 关键修复：注册 transcription_result 处理器（仅处理 voice_call 场景）
    this.registerMessageHandler('transcription_result', (data) => {
        const scenario = data.scenario || 'voice_recording';
        
        if (scenario === 'voice_call') {
            // 语音实时对话：使用独立显示逻辑
            this.handleVoiceCallTranscription(data);
        } else {
            // 录音聊天：不处理，交给 voice_recorder_enhanced.js
            window.controlledLog?.log('收到录音聊天转录结果，跳过语音实时对话处理');
        }
    });
}
```

## 关键设计要点

### 1. 场景区分机制

- **后端**：在 `transcription_result` 消息中添加 `scenario` 字段
  - `voice_call`: 语音实时对话
  - `voice_recording`: 录音聊天（默认，保持兼容）

- **前端**：根据 `scenario` 字段选择处理路径
  - `voice_call` → `voice_websocket_manager.js` 处理 → 更新独立显示存储
  - `voice_recording` → `voice_recorder_enhanced.js` 处理 → 更新 `voice-transcription-store-server` → 触发文本聊天

### 2. 隔离机制

- **独立存储**：`voice-call-transcription-display` Store
  - 不连接任何 Dash 回调的 Input
  - 只能通过 `dash_clientside.set_props` 更新
  - 不影响 `messages` store
  - 不触发 `handle_chat_interactions` 回调

- **独立UI**：推荐使用悬浮面板（方案A）
  - 悬浮在聊天历史上方
  - 不占用固定空间
  - 可以最小化或关闭
  - 不影响主聊天历史滚动

### 3. 性能优化

- **累积更新**：使用队列累积待更新消息，防抖批量处理，避免数据丢失
- **限制数量**：
  - Store 中最多保留50条消息（`max_messages`）
  - UI显示只保留最近的10条消息（悬浮面板限制）
- **非流式显示**：整句渲染，不逐字显示，避免闪烁和性能问题
- **异步处理**：文本更新不影响音频流处理的优先级

### 4. 消息保存策略

- **默认不保存**：避免干扰正常聊天流程
- **可选保存**：通过配置项 `VOICE_CALL_SAVE_TO_DATABASE` 控制
- **延迟保存**：在语音实时对话结束时统一保存
- **标记区分**：保存时添加 `source: 'voice_call'` 标记

### 5. 可配置性

- **后端配置（yychat项目）**：
  ```python
  VOICE_CALL_SEND_TRANSCRIPTION = True  # 是否发送transcription_result
  VOICE_CALL_INCLUDE_ASSISTANT_TEXT = True  # 是否包含AI回复文本
  ```

- **前端配置（yyAsistant项目）**：
  ```python
  VOICE_CALL_SHOW_TRANSCRIPTION = True  # 是否显示文本
  VOICE_CALL_SAVE_TO_DATABASE = False  # 是否保存到数据库（默认不保存）
  VOICE_CALL_AUTO_SAVE_ON_END = True  # 对话结束时是否自动保存
  VOICE_CALL_MAX_DISPLAY_MESSAGES = 50  # 最大显示消息数
  VOICE_CALL_TRANSCRIPTION_DEBOUNCE = 500  # 防抖时间（毫秒）
  VOICE_CALL_STREAMING_DISPLAY = False  # 是否流式显示（建议False）
  ```

## 实施步骤

### 阶段0：方案优化（必须先完成）
1. **修改 `voice_recorder_enhanced.js`**：添加场景检查
   - 在 `handleTranscriptionResult` 中检查 `scenario`
   - 如果是 `voice_call`，直接返回，不处理

2. **修改 `voice_websocket_manager.js`**：注册处理器
   - 在 `registerMessageHandlers` 中注册 `transcription_result` 处理器
   - 只处理 `voice_call` 场景的转录结果

3. **改进防抖机制**：使用累积更新
   - 实现 `pendingVoiceCallMessages` 队列
   - 批量处理，避免数据丢失

### 阶段1：后端支持（yychat项目）
1. 修改 `transcription_result` 消息格式，添加 `scenario` 字段
2. 添加配置项 `VOICE_CALL_SEND_TRANSCRIPTION`
3. 在语音实时对话处理中，根据配置决定是否发送 `transcription_result`
4. （可选）添加 `assistant_text` 字段，包含AI回复文本

### 阶段2：前端基础支持
1. **添加配置项**：在 `VoiceConfig` 中添加相关配置
2. **添加独立Store**：`voice-call-transcription-display`
3. **修改 `voice_websocket_manager.js`**：
   - 实现 `handleVoiceCallTranscription` 方法
   - 实现累积更新机制
   - 实现 `updateVoiceCallTextDisplay` 方法（非流式显示）
   - 在 `startVoiceCall` 和 `stopVoiceCall` 中管理显示

### 阶段3：UI显示
1. **选择UI方案**：推荐方案A（悬浮面板）
2. **添加显示组件**：在 `views/core_pages/chat.py` 中添加
3. **添加显示控制**：显示/隐藏、最小化、关闭按钮
4. **实现Dash回调**（可选）：用于更新UI，但不触发业务逻辑

### 阶段4：消息保存（可选）
1. 添加保存API端点（如果需要前端控制）
2. 实现 `saveVoiceCallMessages` 方法
3. 在 `stopVoiceCall` 中调用保存（如果启用）

### 阶段5：测试和优化
1. **功能测试**：
   - 测试录音聊天功能（确保不受影响）
   - 测试语音实时对话功能（确保正常工作）
   - 测试文本显示功能（非流式显示）
   - 测试消息保存功能（如果启用）

2. **性能测试**：
   - 测试累积更新机制（避免数据丢失）
   - 测试内存使用（消息数量限制）
   - 测试防抖性能（不影响音频流）

3. **集成测试**：
   - 测试场景切换（录音聊天 ↔ 语音实时对话）
   - 测试并发操作（同时进行多种聊天方式）

## 风险评估

### 低风险项
- ✅ 添加新 Store 组件（不影响现有功能）
- ✅ 添加场景区分逻辑（向后兼容）
- ✅ UI显示组件（可选，不影响核心功能）
- ✅ 非流式显示（性能更好，风险更低）
- ✅ 消息保存默认关闭（不干扰现有流程）

### 中风险项
- ⚠️ 后端消息格式修改（需要确保向后兼容）
  - **风险**：如果 `scenario` 字段处理不当，可能导致录音聊天失效
  - **缓解**：`scenario` 字段可选，默认为 `voice_recording`，向后兼容

- ⚠️ 前端消息处理冲突（需要确保场景区分正确）
  - **风险**：`voice_recorder_enhanced.js` 和 `voice_websocket_manager.js` 可能重复处理
  - **缓解**：必须在两个文件中都添加场景检查，确保不会重复处理

- ⚠️ 数据累积问题（需要限制消息数量）
  - **风险**：如果消息数量不受限制，可能导致内存问题
  - **缓解**：Store 限制50条，UI显示限制10条

### 高风险项（已解决）
- ❌ **消息处理冲突**（阶段0必须完成）
  - **风险**：两个处理器可能同时处理同一条消息
  - **解决方案**：在 `voice_recorder_enhanced.js` 中添加场景检查，跳过 `voice_call`

- ❌ **防抖数据丢失**（已改进）
  - **风险**：简单的防抖可能导致中间数据丢失
  - **解决方案**：使用累积更新机制，批量处理

### 防范措施
1. **向后兼容**：
   - `scenario` 字段可选，默认为 `voice_recording`
   - 现有功能完全不受影响

2. **渐进式实现**：
   - **阶段0必须完成**：解决消息处理冲突和防抖问题
   - 先实现基础功能，再添加UI
   - 最后添加保存功能（可选）

3. **充分测试**：
   - 测试录音聊天功能（确保不受影响）
   - 测试语音实时对话功能（确保正常工作）
   - 测试场景切换（确保不会冲突）

4. **配置开关**：
   - 默认保守（不保存、不流式显示）
   - 可以逐步开启测试

5. **数据限制**：
   - Store 限制50条消息
   - UI显示限制10条消息
   - 自动清理旧消息

## 总结

这个方案通过以下方式解决了核心问题：

1. **完全隔离**：
   - 使用独立的存储 `voice-call-transcription-display`，不触发文本聊天逻辑
   - 独立UI组件（推荐悬浮面板），不干扰主聊天历史显示
   - 不写入 `messages` store，不触发 `handle_chat_interactions` 回调

2. **场景区分**：
   - 后端添加 `scenario` 字段区分场景
   - 前端 `voice_recorder_enhanced.js` 和 `voice_websocket_manager.js` 分别处理对应场景
   - 确保不会重复处理或冲突

3. **非流式显示**：
   - 整句显示，避免闪烁
   - 使用累积更新机制，避免数据丢失
   - 限制消息数量，保持性能

4. **消息保存策略**：
   - 默认不保存，避免干扰
   - 可选保存，通过配置控制
   - 延迟保存，对话结束时统一保存
   - 标记区分，保存时添加 `source: 'voice_call'`

5. **UI集成**：
   - 推荐悬浮面板方案（方案A）
   - 不占用固定空间，不影响聊天历史显示
   - 可以最小化或关闭

6. **性能优化**：
   - 累积更新机制，避免数据丢失
   - 限制消息数量（Store: 50条，UI: 10条）
   - 防抖批量处理（500ms）
   - 非流式显示，整句渲染

7. **向后兼容**：
   - `scenario` 字段可选，默认为 `voice_recording`
   - 现有功能完全不受影响
   - 配置项默认值保守（默认不保存）

**核心保证**：**语音实时对话的文本显示完全独立于文本聊天的消息系统，不会造成任何流程混乱，也不会自动保存到数据库（除非明确配置）**。

