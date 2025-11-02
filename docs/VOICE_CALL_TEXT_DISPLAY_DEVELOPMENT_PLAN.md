# 语音实时对话文本显示功能 - 详细开发计划

## 概述

本计划将分阶段实施语音实时对话文本显示功能，每个阶段包含具体的文件修改、代码位置和测试步骤。

---

## 阶段0：方案优化（必须先完成）

### 目标
解决消息处理冲突和防抖数据丢失问题，确保基础架构稳定。

---

### 步骤 0.1：修改 `voice_recorder_enhanced.js` - 添加场景检查

**文件路径**：`yyAsistant/assets/js/voice_recorder_enhanced.js`

**修改位置**：`handleTranscriptionResult` 方法（约第670行）

**修改前代码**：
```javascript
handleTranscriptionResult(data) {
    window.controlledLog?.log('收到转录结果:', data);
    
    if (data.text && data.text.trim()) {
        // ... 现有处理逻辑 ...
    }
}
```

**修改后代码**：
```javascript
handleTranscriptionResult(data) {
    window.controlledLog?.log('收到转录结果:', data);
    
    // 🔧 关键修复：检查场景类型
    const scenario = data.scenario || 'voice_recording';
    
    if (scenario === 'voice_call') {
        // 语音实时对话：不处理，交给 voice_websocket_manager.js
        window.controlledLog?.log('收到语音实时对话转录结果，跳过录音聊天处理');
        return;
    }
    
    // 录音聊天：使用现有逻辑（voice_recording 场景）
    if (data.text && data.text.trim()) {
        // ... 现有处理逻辑保持不变 ...
    }
}
```

**验证点**：
- ✅ 如果是 `voice_call` 场景，直接返回，不执行后续逻辑
- ✅ 如果是 `voice_recording` 场景（或未指定），使用现有逻辑
- ✅ 不影响现有录音聊天功能

**测试步骤**：
1. 启动录音聊天，发送音频
2. 验证 `transcription_result` 正常触发文本聊天流程
3. 验证控制台日志显示正确的场景类型

---

### 步骤 0.2：修改 `voice_websocket_manager.js` - 注册 transcription_result 处理器

**文件路径**：`yyAsistant/assets/js/voice_websocket_manager.js`

**修改位置1**：`registerMessageHandlers` 方法（查找方法定义位置，约第1490行附近）

**需要确认的方法结构**：
```javascript
registerMessageHandlers() {
    // ... 现有处理器注册 ...
    
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

**修改位置2**：`handleMessage` 方法（约第1474行）

**检查是否已有 transcription_result 处理**：
- 如果已有，需要添加场景检查
- 如果没有，需要添加处理器注册

**验证点**：
- ✅ `transcription_result` 消息被正确路由
- ✅ `voice_call` 场景由 `handleVoiceCallTranscription` 处理
- ✅ `voice_recording` 场景被跳过（由 `voice_recorder_enhanced.js` 处理）

**测试步骤**：
1. 启动语音实时对话
2. 验证 `transcription_result` 被正确接收
3. 验证日志显示正确的处理路径

---

### 步骤 0.3：改进防抖机制 - 实现累积更新

**文件路径**：`yyAsistant/assets/js/voice_websocket_manager.js`

**新增属性**：在 `constructor` 或类属性中添加（约第1-50行）
```javascript
constructor() {
    // ... 现有属性 ...
    
    // 新增：语音实时对话文本显示相关
    this.pendingVoiceCallMessages = [];  // 待更新消息队列
    this.voiceCallDisplayUpdateTimer = null;  // 防抖定时器
    this.voiceCallTranscriptionDisplay = null;  // 当前显示数据
}
```

**新增方法1**：`debounceUpdateVoiceCallDisplay`（在类中添加新方法）
```javascript
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
```

**新增方法2**：`handleVoiceCallTranscription`（在类中添加新方法）
```javascript
// 处理语音实时对话的转录结果（非流式显示，整句显示）
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
```

**验证点**：
- ✅ 消息被累积到队列中，不会丢失
- ✅ 防抖定时器正确清理
- ✅ 消息数量限制生效（最多50条）

**测试步骤**：
1. 快速发送多条转录结果
2. 验证所有消息都被累积
3. 验证防抖后批量更新
4. 验证消息数量限制

---

## 阶段1：后端支持（yychat项目）

### 目标
在后端添加场景区分和配置支持。

---

### 步骤 1.1：添加后端配置项

**文件路径**：`yychat/config/realtime_config.py`

**修改位置**：`RealtimeConfig` 类中（约第11-75行）

**新增配置**：
```python
class RealtimeConfig:
    """实时语音配置类"""
    
    def __init__(self):
        # ... 现有配置 ...
        
        # 新增：语音实时对话文本显示配置
        self.VOICE_CALL_SEND_TRANSCRIPTION = True  # 是否发送transcription_result
        self.VOICE_CALL_INCLUDE_ASSISTANT_TEXT = True  # 是否包含AI回复文本
```

**或者从环境变量读取**：
```python
self.VOICE_CALL_SEND_TRANSCRIPTION = os.getenv('VOICE_CALL_SEND_TRANSCRIPTION', 'true').lower() == 'true'
self.VOICE_CALL_INCLUDE_ASSISTANT_TEXT = os.getenv('VOICE_CALL_INCLUDE_ASSISTANT_TEXT', 'true').lower() == 'true'
```

**验证点**：
- ✅ 配置项可以被正确读取
- ✅ 默认值合理

**测试步骤**：
1. 启动后端服务
2. 验证配置项被正确加载
3. 验证日志显示配置值

---

### 步骤 1.2：修改 `realtime_handler.py` - 添加场景字段

**文件路径**：`yychat/core/realtime_handler.py`

**修改位置1**：`_handle_audio_input` 方法中发送 `transcription_result` 的位置（约第190-196行）

**修改前代码**：
```python
# 发送转录结果
await websocket_manager.send_message(client_id, {
    "type": "transcription_result",
    "text": transcribed_text,
    "timestamp": time.time(),
    "client_id": client_id
})
```

**修改后代码**：
```python
# 发送转录结果（添加场景字段）
if self.config.VOICE_CALL_SEND_TRANSCRIPTION:
    await websocket_manager.send_message(client_id, {
        "type": "transcription_result",
        "text": transcribed_text,
        "timestamp": time.time(),
        "client_id": client_id,
        "scenario": "voice_call",  # 新增：标识场景类型
        "message_id": f"voice-call-{client_id}-{int(time.time() * 1000)}"  # 可选：消息ID
    })
```

**注意**：需要确认 `self.config` 是否正确引用 `RealtimeConfig`

**验证点**：
- ✅ `transcription_result` 消息包含 `scenario: "voice_call"` 字段
- ✅ 配置项控制是否发送
- ✅ 不影响其他场景的消息

**测试步骤**：
1. 启动语音实时对话
2. 发送音频
3. 验证 WebSocket 消息包含 `scenario` 字段
4. 验证配置项控制是否生效

---

### 步骤 1.3：修改 `message_router.py` - 区分场景

**文件路径**：`yychat/core/message_router.py`

**修改位置**：`handle_audio_input` 函数中发送 `transcription_result` 的位置（约第317-321行）

**问题**：需要确认 `handle_audio_input` 是在哪个场景下被调用
- 如果是录音聊天场景，应该添加 `scenario: "voice_recording"`
- 如果是语音实时对话场景，应该添加 `scenario: "voice_call"`

**修改后代码**：
```python
# 下行：转写结果
await websocket_manager.send_message(client_id, {
    "type": "transcription_result",
    "text": text,
    "timestamp": __import__("time").time(),
    "scenario": "voice_recording",  # 新增：标识场景类型（录音聊天）
})
```

**验证点**：
- ✅ 录音聊天场景的消息包含 `scenario: "voice_recording"`
- ✅ 与语音实时对话的场景区分清楚

**测试步骤**：
1. 启动录音聊天
2. 发送音频
3. 验证消息包含 `scenario: "voice_recording"`

---

### 步骤 1.4：（可选）添加 AI 回复文本支持

**文件路径**：`yychat/core/realtime_handler.py`

**修改位置**：`_handle_audio_input` 方法中，如果需要包含 AI 回复文本（约第197行之后）

**前提**：需要确认语音实时对话是否生成文本回复

**修改逻辑**：
1. 如果配置了 `VOICE_CALL_INCLUDE_ASSISTANT_TEXT`
2. 且生成了 AI 回复文本
3. 在 `transcription_result` 消息中添加 `assistant_text` 字段

**修改后代码**：
```python
# 发送转录结果
message = {
    "type": "transcription_result",
    "text": transcribed_text,
    "timestamp": time.time(),
    "client_id": client_id,
    "scenario": "voice_call",
    "message_id": f"voice-call-{client_id}-{int(time.time() * 1000)}"
}

# 如果配置包含AI回复文本
if self.config.VOICE_CALL_INCLUDE_ASSISTANT_TEXT:
    # 获取AI回复文本（需要根据实际实现获取）
    assistant_text = await self._get_assistant_text(transcribed_text)
    if assistant_text:
        message["assistant_text"] = assistant_text
        message["assistant_message_id"] = f"voice-call-assistant-{client_id}-{int(time.time() * 1000)}"

await websocket_manager.send_message(client_id, message)
```

**验证点**：
- ✅ 配置项控制是否包含 AI 回复文本
- ✅ AI 回复文本正确包含在消息中

**测试步骤**：
1. 启用 `VOICE_CALL_INCLUDE_ASSISTANT_TEXT`
2. 发送音频
3. 验证消息包含 `assistant_text` 字段

---

## 阶段2：前端基础支持（yyAsistant项目）

### 目标
在前端添加配置项、Store 和基础处理逻辑。

---

### 步骤 2.1：添加前端配置项

**文件路径**：`yyAsistant/configs/voice_config.py`

**修改位置**：`VoiceConfig` 类中（约第5-87行）

**新增配置**：
```python
class VoiceConfig:
    """语音功能配置类"""
    
    # ... 现有配置 ...
    
    # 新增：语音实时对话文本显示配置
    VOICE_CALL_SHOW_TRANSCRIPTION = True  # 是否显示转录文本（前端配置）
    VOICE_CALL_SAVE_TO_DATABASE = False  # 是否保存到数据库（默认不保存，避免干扰）
    VOICE_CALL_AUTO_SAVE_ON_END = True  # 对话结束时是否自动保存（如果VOICE_CALL_SAVE_TO_DATABASE=True）
    VOICE_CALL_MAX_DISPLAY_MESSAGES = 50  # 最大显示消息数（Store限制）
    VOICE_CALL_TRANSCRIPTION_DEBOUNCE = 500  # 文本更新防抖时间（毫秒）
    VOICE_CALL_STREAMING_DISPLAY = False  # 是否流式显示（建议False，整句显示）
```

**验证点**：
- ✅ 配置项可以被正确读取
- ✅ 默认值合理

**测试步骤**：
1. 启动前端服务
2. 验证配置项被正确加载
3. 在 JavaScript 中验证可以访问配置（`window.voiceConfig`）

---

### 步骤 2.2：添加独立 Store 组件

**文件路径**：`yyAsistant/views/core_pages/chat.py`

**修改位置**：`_create_state_stores` 函数中（约第301-350行）

**新增 Store**：
```python
def _create_state_stores():
    """创建页面所需的状态存储组件"""
    # ... 现有 Store ...
    
    # 新增：语音实时对话文本显示存储
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
    
    # 在返回列表中添加
    return [
        # ... 现有 Store ...
        voice_call_transcription_display,  # 新增
    ]
```

**验证点**：
- ✅ Store 被正确创建
- ✅ 初始数据结构正确
- ✅ ID 唯一，不与其他 Store 冲突

**测试步骤**：
1. 启动前端服务
2. 验证页面加载时 Store 存在
3. 验证 Store 初始数据正确

---

### 步骤 2.3：完善 `voice_websocket_manager.js` - 实现显示逻辑

**文件路径**：`yyAsistant/assets/js/voice_websocket_manager.js`

**修改位置1**：`updateVoiceCallTextDisplay` 方法（在阶段0.3中已添加，需要完善）

**完整实现**：
```javascript
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
```

**修改位置2**：`startVoiceCall` 方法中初始化显示

**查找方法位置**：搜索 `startVoiceCall` 或 `开始语音实时对话`

**新增代码**：
```javascript
startVoiceCall() {
    // ... 现有代码 ...
    
    // 新增：初始化文本显示
    if (window.dash_clientside && window.dash_clientside.set_props) {
        window.dash_clientside.set_props('voice-call-transcription-display', {
            data: {
                messages: [],
                is_active: true,
                session_id: this.sessionId,
                call_start_time: Date.now(),
                max_messages: 50,
                created_at: Date.now()
            }
        });
    }
    
    // 显示文本显示区域（如果有）
    const displayElement = document.getElementById('voice-call-text-display');
    if (displayElement && window.voiceConfig && window.voiceConfig.VOICE_CALL_SHOW_TRANSCRIPTION) {
        displayElement.style.display = 'block';
    }
    
    // 重置显示数据
    this.voiceCallTranscriptionDisplay = null;
    this.pendingVoiceCallMessages = [];
}
```

**修改位置3**：`stopVoiceCall` 方法中清理显示

**查找方法位置**：搜索 `stopVoiceCall` 或 `停止语音实时对话`

**新增代码**：
```javascript
stopVoiceCall() {
    // ... 现有代码 ...
    
    // 隐藏文本显示区域
    const displayElement = document.getElementById('voice-call-text-display');
    if (displayElement) {
        displayElement.style.display = 'none';
    }
    
    // 更新Store状态为不活跃
    if (window.dash_clientside && window.dash_clientside.set_props) {
        const currentDisplay = this.voiceCallTranscriptionDisplay || {
            messages: [],
            is_active: false,
            session_id: this.sessionId,
            max_messages: 50,
            created_at: Date.now()
        };
        currentDisplay.is_active = false;
        
        window.dash_clientside.set_props('voice-call-transcription-display', {
            data: currentDisplay
        });
    }
    
    // 可选保存消息到数据库（如果启用）
    if (window.voiceConfig && window.voiceConfig.VOICE_CALL_SAVE_TO_DATABASE) {
        this.saveVoiceCallMessages();
    }
}
```

**验证点**：
- ✅ UI 显示正确渲染
- ✅ 消息数量限制生效（最多10条显示）
- ✅ 非流式显示（整句渲染）
- ✅ HTML 转义防止 XSS

**测试步骤**：
1. 启动语音实时对话
2. 发送多条音频
3. 验证文本正确显示
4. 验证消息数量限制
5. 验证关闭对话时显示区域隐藏

---

## 阶段3：UI显示

### 目标
添加独立的文本显示组件，集成到现有界面。

---

### 步骤 3.1：添加悬浮面板组件（方案A - 推荐）

**文件路径**：`yyAsistant/views/core_pages/chat.py`

**修改位置1**：`_create_content_area` 函数中，`chat_history` 之前（约第143-289行）

**新增组件代码**：
```python
def _create_content_area():
    """创建右侧聊天内容区域"""
    # ... 现有代码（chat_header） ...
    
    # 新增：语音实时对话文本显示悬浮面板
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
    
    # ... 返回组合 ...
```

**验证点**：
- ✅ 组件正确添加到布局
- ✅ 默认隐藏
- ✅ 定位正确（相对于 chat_history）

**测试步骤**：
1. 启动前端服务
2. 验证页面加载
3. 验证悬浮面板存在但隐藏
4. 验证布局不被打乱

---

### 步骤 3.2：添加关闭按钮回调（可选）

**文件路径**：`yyAsistant/callbacks/core_pages_c/chat_c.py` 或新建 `callbacks/voice_call_display_c.py`

**新建文件**：`callbacks/voice_call_display_c.py`

**代码**：
```python
from dash import Input, Output, callback, no_update
from dash.exceptions import PreventUpdate
from utils.log import log

@callback(
    Output('voice-call-text-display', 'style'),
    Input('voice-call-text-close-btn', 'n_clicks'),
    prevent_initial_call=True
)
def close_voice_call_text_display(n_clicks):
    """关闭语音实时对话文本显示面板"""
    if n_clicks:
        log.info("关闭语音实时对话文本显示面板")
        return {'display': 'none'}
    raise PreventUpdate
```

**在 `app.py` 中注册**：
```python
# 在导入回调的地方添加
import callbacks.voice_call_display_c  # noqa: F401
```

**验证点**：
- ✅ 关闭按钮可以隐藏面板
- ✅ 不影响其他功能

**测试步骤**：
1. 启动语音实时对话
2. 点击关闭按钮
3. 验证面板隐藏

---

### 步骤 3.3：（可选）添加 Dash 回调更新 UI

**文件路径**：`yyAsistant/callbacks/voice_call_display_c.py`

**代码**：
```python
@callback(
    Output('voice-call-text-content', 'children'),
    Input('voice-call-transcription-display', 'data'),
    prevent_initial_call=True
)
def update_voice_call_text_display(display_data):
    """仅用于更新UI显示，不触发任何业务逻辑"""
    if not display_data or not display_data.get('messages'):
        return []
    
    messages = display_data['messages']
    # 只显示最近的10条
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    # 生成UI组件（可选，如果使用Dash组件）
    # 注意：推荐使用JavaScript直接更新DOM，性能更好
    return []  # 暂时返回空，由JavaScript更新
```

**注意**：推荐使用JavaScript直接更新DOM，不使用Dash回调，性能更好。

**验证点**：
- ✅ 回调不触发业务逻辑
- ✅ 不影响其他功能

---

## 阶段4：消息保存（可选）

### 目标
实现语音实时对话消息的可选保存功能。

---

### 步骤 4.1：实现保存方法（前端）

**文件路径**：`yyAsistant/assets/js/voice_websocket_manager.js`

**修改位置**：`stopVoiceCall` 方法中（阶段2.3已添加调用）

**新增方法**：
```javascript
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
        } else {
            console.error('保存失败:', response.statusText);
        }
    } catch (error) {
        console.error('保存语音实时对话消息失败:', error);
    }
}
```

**验证点**：
- ✅ 保存方法正确调用
- ✅ 错误处理正确

---

### 步骤 4.2：添加后端 API 端点

**文件路径**：`yyAsistant/routes/` 或 `yyAsistant/app.py`

**新增路由**：
```python
@app.route('/api/voice-call/save-messages', methods=['POST'])
@login_required
def save_voice_call_messages():
    """保存语音实时对话消息到数据库"""
    from configs.voice_config import VoiceConfig
    from models.conversations import Conversations
    import datetime
    
    if not VoiceConfig.VOICE_CALL_SAVE_TO_DATABASE:
        return jsonify({'error': '语音实时对话消息保存未启用'}), 400
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        messages = data.get('messages', [])
        
        if not session_id or not messages:
            return jsonify({'error': '参数不完整'}), 400
        
        conv = Conversations.get_conversation_by_conv_id(session_id)
        if not conv:
            return jsonify({'error': '会话不存在'}), 404
        
        existing_messages = conv.conv_memory.get('messages', []) if conv.conv_memory else []
        
        # 添加语音实时对话消息，标记来源
        for msg in messages:
            existing_messages.append({
                'role': msg.get('role'),
                'content': msg.get('text'),
                'timestamp': datetime.datetime.fromtimestamp(
                    msg.get('timestamp', time.time())
                ).strftime('%Y-%m-%d %H:%M:%S'),
                'id': msg.get('message_id'),
                'source': 'voice_call'  # 标记为语音实时对话
            })
        
        Conversations.update_conversation_by_conv_id(
            session_id,
            conv_memory={'messages': existing_messages}
        )
        
        log.info(f"✅ 语音实时对话消息已保存到数据库: {session_id}, 消息数: {len(messages)}")
        return jsonify({'success': True, 'count': len(messages)})
    except Exception as e:
        log.error(f"保存语音实时对话消息失败: {e}")
        return jsonify({'error': str(e)}), 500
```

**验证点**：
- ✅ API端点正确注册
- ✅ 权限检查正确
- ✅ 保存逻辑正确
- ✅ 错误处理完善

**测试步骤**：
1. 启用保存配置
2. 进行语音实时对话
3. 结束对话
4. 验证消息保存到数据库
5. 验证消息包含 `source: 'voice_call'` 标记

---

## 阶段5：测试和优化

### 目标
全面测试功能，确保稳定性和性能。

---

### 步骤 5.1：功能测试

**测试项1：录音聊天功能不受影响**
- 启动录音聊天
- 发送音频
- 验证转录结果正常触发文本聊天流程
- 验证消息正常保存到数据库
- 验证日志显示 `scenario: "voice_recording"`

**测试项2：语音实时对话功能正常**
- 启动语音实时对话
- 发送音频
- 验证转录结果正确显示
- 验证文本显示区域正确显示/隐藏
- 验证日志显示 `scenario: "voice_call"`

**测试项3：场景切换**
- 先进行录音聊天，验证正常
- 切换到语音实时对话，验证正常
- 切换回录音聊天，验证正常
- 验证不会冲突

**测试项4：消息保存（如果启用）**
- 启用保存配置
- 进行语音实时对话
- 结束对话
- 验证消息保存到数据库
- 验证消息包含 `source: 'voice_call'` 标记

---

### 步骤 5.2：性能测试

**测试项1：累积更新机制**
- 快速发送多条转录结果（10条以上）
- 验证所有消息都被累积
- 验证防抖后批量更新
- 验证消息数量限制生效（Store: 50条，UI: 10条）

**测试项2：内存使用**
- 长时间进行语音实时对话
- 验证消息数量不超过限制
- 验证旧消息被正确清理
- 验证内存使用稳定

**测试项3：防抖性能**
- 验证防抖不影响音频流处理
- 验证防抖时间合理（500ms）
- 验证更新频率适中

---

### 步骤 5.3：集成测试

**测试项1：并发操作**
- 同时进行多种聊天方式
- 验证不会冲突
- 验证状态管理正确

**测试项2：页面刷新**
- 进行语音实时对话
- 刷新页面
- 验证状态正确恢复
- 验证Store数据正确

**测试项3：错误处理**
- 模拟网络错误
- 模拟后端错误
- 验证错误处理正确
- 验证不影响其他功能

---

## 开发顺序总结

### 必须按顺序完成的阶段

1. **阶段0（必须先完成）**：解决消息处理冲突和防抖问题
2. **阶段1（后端）**：添加场景区分和配置支持
3. **阶段2（前端基础）**：添加配置项、Store 和基础处理逻辑
4. **阶段3（UI显示）**：添加文本显示组件
5. **阶段4（可选）**：实现消息保存功能
6. **阶段5（测试）**：全面测试和优化

### 每个阶段的依赖关系

- 阶段0 → 阶段1：阶段0确保前端可以区分场景
- 阶段1 → 阶段2：阶段1提供后端场景字段
- 阶段2 → 阶段3：阶段2提供Store和基础逻辑
- 阶段3 → 阶段4：阶段3提供UI显示
- 阶段4 → 阶段5：阶段4提供保存功能
- 所有阶段 → 阶段5：全面测试

---

## 预估工作量

- **阶段0**：2-3小时
- **阶段1**：2-3小时
- **阶段2**：3-4小时
- **阶段3**：2-3小时
- **阶段4**：1-2小时（可选）
- **阶段5**：3-4小时

**总计**：约13-19小时（不含阶段4约12-17小时）

---

## 注意事项

1. **必须完成阶段0**：解决消息处理冲突是关键，否则会出现重复处理
2. **配置项默认值**：建议保守默认值（不保存、不流式显示）
3. **向后兼容**：确保不影响现有功能
4. **性能优先**：限制消息数量，使用累积更新
5. **错误处理**：完善错误处理，避免影响其他功能

---

## 验收标准

### 基本功能
- ✅ 语音实时对话可以显示转录文本
- ✅ 录音聊天功能不受影响
- ✅ 场景切换正常

### 性能要求
- ✅ 消息数量限制生效
- ✅ 防抖机制正常工作
- ✅ 不影响音频流处理

### 稳定性要求
- ✅ 错误处理完善
- ✅ 不会导致页面崩溃
- ✅ 向后兼容

### 可选功能（如果启用）
- ✅ 消息保存功能正常
- ✅ 保存的消息包含正确标记

