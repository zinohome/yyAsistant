# TTS停止播放按钮完整实现方案

## 一、需求分析

### 1.1 功能需求
- 在TTS播放时（录音聊天和文本聊天场景），在AI消息的操作栏中显示一个喇叭图标按钮
- 点击按钮可以立即停止当前消息的TTS播放
- 停止后，即使WebSocket继续接收该消息的音频数据，也不会播放

### 1.2 技术挑战
1. **简单音频播放机制**：使用`playSimpleTTS` + `simpleQueue`队列
2. **WebSocket持续接收**：停止后，服务端可能继续发送音频片段
3. **消息ID跟踪**：需要准确识别并停止特定消息的TTS
4. **按钮动态显示**：需要根据播放状态动态显示/隐藏按钮

## 二、完整实现方案

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    TTS停止播放架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  【前端】                                                     │
│  ┌──────────────────┐      ┌──────────────────────┐         │
│  │ smart_message_   │─────▶│ 客户端 JavaScript    │         │
│  │ actions.py       │      │ 监听按钮点击         │         │
│  │ 创建停止按钮     │      │                      │         │
│  └──────────────────┘      └──────────┬───────────┘         │
│                                        │                      │
│                                        ▼                      │
│  ┌──────────────────────────────────────────────────┐         │
│  │ voice_player_enhanced.js                         │         │
│  │ - stoppedSimpleTTS Map: 跟踪停止的消息ID        │         │
│  │ - simpleCurrentSource: 当前播放的音频源         │         │
│  │ - stopSimpleTTS(): 停止播放方法                │         │
│  └──────────────────────────────────────────────────┘         │
│                                                               │
│  【拦截机制】                                                  │
│  ┌──────────────────┐      ┌──────────────────────┐         │
│  │ handleAudioStream│─────▶│ 检查 stoppedSimpleTTS │         │
│  │ (入口拦截)       │      │ 如果已停止，丢弃音频  │         │
│  └──────────────────┘      └──────────────────────┘         │
│                                        │                      │
│                                        ▼                      │
│  ┌──────────────────┐      ┌──────────────────────┐         │
│  │ playSimpleTTS    │─────▶│ 二次检查停止标志      │         │
│  │ (二次检查)       │      │ 如果已停止，不处理    │         │
│  └──────────────────┘      └──────────────────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心机制

#### 2.2.1 停止标志跟踪机制
- 使用`Map<messageId, boolean>`跟踪每个消息的停止状态
- 在WebSocket接收音频数据的入口处检查标志
- 在播放处理的关键节点二次检查

#### 2.2.2 三层拦截机制
1. **第一层：handleAudioStream入口拦截**
   - 检查`stoppedSimpleTTS.get(messageId)`
   - 如果已停止，直接`return`，丢弃音频数据

2. **第二层：playSimpleTTS二次检查**
   - 在解码音频数据前再次检查停止标志
   - 避免不必要的解码处理

3. **第三层：playSimpleAudioBuffer播放前检查**
   - 在开始播放前最后检查
   - 确保被停止的消息不会播放

## 三、详细实现步骤

### 步骤1：修改 voice_player_enhanced.js - 添加停止标志跟踪

**文件位置**：`assets/js/voice_player_enhanced.js`

#### 1.1 在构造函数中添加停止标志
```javascript
constructor() {
    // ... 现有代码 ...
    
    // 🔧 新增：简单TTS停止标志跟踪
    this.stoppedSimpleTTS = new Map(); // messageId -> true/false
    this.simpleCurrentSource = null;   // 当前简单播放的音频源
    
    // ... 其他代码 ...
}
```

#### 1.2 修改 handleAudioStream - 添加入口拦截
```javascript
handleAudioStream(data) {
    try {
        const messageId = data.message_id || 'unknown';
        const sessionId = data.session_id || null;
        const codec = data.codec || 'audio/mpeg';
        const base64 = data.audio || data.audio_data;
        const seq = typeof data.seq === 'number' ? data.seq : null;

        if (!base64) {
            return;
        }

        // 🔧 关键修复：入口拦截 - 检查该消息是否已停止
        if (this.stoppedSimpleTTS && this.stoppedSimpleTTS.get(messageId)) {
            window.controlledLog?.log('🛑 消息已停止，丢弃音频数据:', messageId);
            return; // 直接返回，不处理该音频
        }

        // 判断场景类型
        const isRecordingChat = sessionId && sessionId.includes('conv-');
        const isVoiceCall = sessionId && !sessionId.includes('conv-');
        const isTextChat = messageId && messageId.includes('ai-message');
        
        window.controlledLog?.log(`🎵 音频流场景判断: 录音聊天=${isRecordingChat}, 语音通话=${isVoiceCall}, 文本聊天=${isTextChat}`);
        
        if (isRecordingChat || isTextChat) {
            // 录音聊天TTS 或 文本聊天TTS：简单按序播放，不使用分片管理
            window.controlledLog?.log('🎧 聊天TTS（录音/文本），简单按序播放');
            this.playSimpleTTS(base64, messageId, seq);
        } else if (isVoiceCall) {
            // 语音通话TTS：使用复杂分片管理
            window.controlledLog?.log('🎤 语音通话TTS，使用分片管理');
            this.playVoiceCallTTS(base64, messageId, sessionId, codec, seq);
        } else {
            // 未知场景：默认简单播放
            window.controlledLog?.log('❓ 未知场景TTS，默认简单播放');
            this.playSimpleTTS(base64, messageId);
        }
    } catch (error) {
        console.error('处理音频流失败:', error);
    }
}
```

#### 1.3 修改 playSimpleTTS - 添加二次检查
```javascript
async playSimpleTTS(base64, messageId, seq = null) {
    // 🔧 关键修复：二次检查停止标志
    if (this.stoppedSimpleTTS && this.stoppedSimpleTTS.get(messageId)) {
        window.controlledLog?.log('🛑 消息已停止，不添加到播放队列:', messageId);
        return; // 不处理该音频
    }
    
    window.controlledLog?.log('🎧 简单TTS播放:', messageId);
    
    try {
        // ... 现有解码代码 ...
        
        // 添加到简单播放队列，确保按序播放
        this.addToSimpleQueue(decodedBuffer, messageId, seq);
        
    } catch (error) {
        console.error('❌ 简单TTS播放失败:', error);
    }
}
```

#### 1.4 修改 playSimpleAudioBuffer - 保存源引用并添加检查
```javascript
async playSimpleAudioBuffer(audioBuffer, messageId = null) {
    // 🔧 关键修复：播放前最后检查停止标志
    if (messageId && this.stoppedSimpleTTS && this.stoppedSimpleTTS.get(messageId)) {
        window.controlledLog?.log('🛑 消息已停止，不播放:', messageId);
        return Promise.resolve(); // 不播放
    }
    
    return new Promise((resolve, reject) => {
        try {
            window.controlledLog?.log('🎧 简单音频播放:', messageId);
            
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            // 🔧 关键修复：保存当前播放的源
            this.simpleCurrentSource = source;
            
            source.buffer = audioBuffer;
            gainNode.gain.value = this.synthesisSettings.volume;
            
            // 连接音频节点
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // 设置播放结束回调
            source.onended = () => {
                window.controlledLog?.log('🎧 简单音频播放完成:', messageId);
                
                // 清除当前播放源
                if (this.simpleCurrentSource === source) {
                    this.simpleCurrentSource = null;
                }
                
                // ... 现有的队列清理和状态更新代码 ...
                
                resolve();
            };
            
            // 开始播放
            source.start();
            window.controlledLog?.log('🎧 简单音频开始播放:', messageId);
            
            // ... 现有的状态指示器代码 ...
            
        } catch (error) {
            console.error('❌ 简单音频播放失败:', error);
            reject(error);
        }
    });
}
```

#### 1.5 添加 stopSimpleTTS 方法
```javascript
/**
 * 停止简单TTS播放（录音聊天和文本聊天）
 * 停止当前播放、清空队列、标记停止、重置状态
 * 
 * @param {string} messageId - 消息ID，如果为null则停止所有正在播放的简单TTS
 */
stopSimpleTTS(messageId = null) {
    window.controlledLog?.log('🛑 停止简单TTS播放:', messageId);
    
    // 如果没有指定消息ID，停止所有正在播放的简单TTS
    if (!messageId) {
        // 找到当前正在播放的消息ID（从simpleQueue中获取）
        if (this.simpleQueue && this.simpleQueue.length > 0) {
            // 获取队列中所有唯一的messageId
            const playingMessageIds = [...new Set(this.simpleQueue.map(item => item.messageId))];
            window.controlledLog?.log('🛑 停止所有正在播放的消息:', playingMessageIds);
            playingMessageIds.forEach(id => {
                this.stoppedSimpleTTS.set(id, true);
            });
        }
    } else {
        // 标记该消息已停止
        this.stoppedSimpleTTS.set(messageId, true);
        window.controlledLog?.log('🛑 标记消息已停止:', messageId);
    }
    
    // 停止当前播放的音频源
    if (this.simpleCurrentSource) {
        try {
            this.simpleCurrentSource.stop(0);
            this.simpleCurrentSource.disconnect();
            window.controlledLog?.log('🛑 简单TTS音频源已停止');
        } catch (error) {
            window.controlledLog?.log('简单TTS音频源已停止');
        }
        this.simpleCurrentSource = null;
    }
    
    // 清空简单播放队列（移除被停止消息的所有音频）
    if (this.simpleQueue) {
        if (messageId) {
            // 只移除指定消息的音频
            const beforeLength = this.simpleQueue.length;
            this.simpleQueue = this.simpleQueue.filter(item => item.messageId !== messageId);
            const afterLength = this.simpleQueue.length;
            window.controlledLog?.log(`🛑 已从队列中移除消息音频: ${messageId}, 队列长度: ${beforeLength} -> ${afterLength}`);
        } else {
            // 清空所有队列
            this.simpleQueue = [];
            window.controlledLog?.log('🛑 简单播放队列已清空');
        }
    }
    
    // 重置播放标志
    this.simplePlaying = false;
    
    // 检查是否还有未停止的消息在播放
    const hasOtherPlaying = this.simpleQueue && this.simpleQueue.length > 0;
    if (!hasOtherPlaying) {
        this.isTtsPlaying = false;
        
        // 隐藏播放状态指示器
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.hide();
        }
    }
    
    // 清理相关流状态（只清理被停止的消息，保留其他消息的）
    if (messageId && this.streamStates.has(messageId)) {
        this.streamStates.delete(messageId);
        window.controlledLog?.log('🛑 清理TTS流状态:', messageId);
    }
    
    // 触发状态更新，重置按钮状态到idle（如果没有其他消息在播放）
    if (!hasOtherPlaying) {
        const currentPath = window.location.pathname;
        const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
        
        if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
            try {
                window.dash_clientside.set_props('button-event-trigger', {
                    data: {type: 'tts_stop', timestamp: Date.now()}
                });
                window.controlledLog?.log('🛑 TTS停止，触发按钮状态重置');
            } catch (setPropsError) {
                console.error('set_props调用失败:', setPropsError);
            }
        }
    }
    
    // 🔧 关键保护机制1：停止标志超时清理（5分钟后自动清理，防止永久阻止播放）
    if (messageId) {
        setTimeout(() => {
            if (this.stoppedSimpleTTS) {
                const wasStopped = this.stoppedSimpleTTS.has(messageId);
                this.stoppedSimpleTTS.delete(messageId);
                if (wasStopped) {
                    window.controlledLog?.log('⏰ 停止标志超时清理:', messageId);
                }
            }
        }, 5 * 60 * 1000); // 5分钟后自动清理
    }
    
    window.controlledLog?.log('✅ 简单TTS播放已停止，状态已重置');
}
```

#### 1.6 在 handleSynthesisComplete 中清理停止标志
```javascript
handleSynthesisComplete(data) {
    const messageId = data.message_id || null;
    
    // 🔧 清理停止标志，允许下次播放（如果用户再次点击重新生成）
    if (messageId && this.stoppedSimpleTTS) {
        const wasStopped = this.stoppedSimpleTTS.has(messageId);
        this.stoppedSimpleTTS.delete(messageId);
        if (wasStopped) {
            window.controlledLog?.log('✅ 合成完成，清理消息停止标志:', messageId);
        }
    }
    
    // ... 现有的其他代码 ...
}
```

#### 1.7 在 processSimpleQueue 中添加停止检查（保护机制2）
```javascript
async processSimpleQueue() {
    // 🔧 关键保护机制2：过滤掉已停止的消息，避免处理已停止的音频
    if (this.simpleQueue && this.simpleQueue.length > 0) {
        const beforeLength = this.simpleQueue.length;
        this.simpleQueue = this.simpleQueue.filter(item => {
            if (this.stoppedSimpleTTS && this.stoppedSimpleTTS.get(item.messageId)) {
                window.controlledLog?.log('🛑 跳过已停止的消息:', item.messageId);
                return false;
            }
            return true;
        });
        const afterLength = this.simpleQueue.length;
        if (beforeLength !== afterLength) {
            window.controlledLog?.log(`🛑 已过滤已停止的消息，队列长度: ${beforeLength} -> ${afterLength}`);
        }
    }
    
    if (this.simplePlaying || !this.simpleQueue || this.simpleQueue.length === 0) {
        return;
    }
    
    // ... 现有的其他代码 ...
}
```

#### 1.8 添加清理停止标志的工具方法（保护机制3）
```javascript
/**
 * 清理指定消息的停止标志（用于消息重新生成等场景）
 * 
 * @param {string} messageId - 消息ID
 */
clearStopFlag(messageId) {
    if (messageId && this.stoppedSimpleTTS) {
        const wasStopped = this.stoppedSimpleTTS.has(messageId);
        this.stoppedSimpleTTS.delete(messageId);
        if (wasStopped) {
            window.controlledLog?.log('✅ 手动清理停止标志:', messageId);
        }
    }
}

/**
 * 清理所有停止标志（用于重置场景）
 */
clearAllStopFlags() {
    if (this.stoppedSimpleTTS) {
        const count = this.stoppedSimpleTTS.size;
        this.stoppedSimpleTTS.clear();
        if (count > 0) {
            window.controlledLog?.log(`✅ 清理所有停止标志，共${count}个`);
        }
    }
}
```

### 步骤2：修改 smart_message_actions.py - 添加停止按钮

**文件位置**：`components/smart_message_actions.py`

#### 2.1 添加停止按钮创建函数
```python
def create_tts_stop_button(message_id):
    """
    创建TTS停止播放按钮
    
    Args:
        message_id: 消息ID
    
    Returns:
        fac.AntdButton: TTS停止按钮
    """
    return fac.AntdButton(
        icon=fac.AntdIcon(icon='antd-sound'),  # 喇叭图标
        id={'type': 'ai-chat-x-stop-tts', 'index': message_id},
        type="text",
        size="small",
        nClicks=0,
        title="停止语音播放",
        style=style(
            fontSize=16, 
            color='#52c41a',  # 绿色，表示正在播放
            padding='4px 8px',
            minWidth='auto',
            height='auto'
        ),
        className="tts-stop-button"  # 添加类名，方便客户端JavaScript选择
    )
```

#### 2.2 修改 create_smart_message_actions 函数
```python
def create_smart_message_actions(message_id, current_state='SUCCESS', is_streaming=False, error_info=None):
    """
    创建智能状态感知的消息操作栏
    保留原有的ai-chat-x-regenerate和ai-chat-x-copy按钮，添加智能功能
    
    Args:
        message_id: 消息ID
        current_state: 当前状态 (SUCCESS, PROCESSING, ERROR)
        is_streaming: 是否正在流式传输
        error_info: 错误信息
    
    Returns:
        fac.AntdRow: 智能操作栏组件
    """
    
    # 保留原有的核心按钮
    core_actions = [
        # ... 现有的重新生成和复制按钮 ...
    ]
    
    # 智能状态感知操作
    smart_actions = []
    
    # 🔧 新增：TTS停止按钮（初始隐藏，通过客户端JavaScript控制显示）
    smart_actions.append(
        html.Div(
            create_tts_stop_button(message_id),
            id={'type': 'tts-stop-button-wrapper', 'index': message_id},
            style={'display': 'none'}  # 初始隐藏
        )
    )
    
    # 流式传输时的进度指示器
    if current_state == 'PROCESSING' and is_streaming:
        smart_actions.append(create_progress_indicator())
    elif current_state == 'ERROR' and error_info:
        smart_actions.append(create_error_tooltip(error_info))
    
    # 状态指示器
    smart_actions.append(create_status_indicator(current_state))
    
    # ... 其他代码 ...
```

### 步骤3：在消息重新生成时清理停止标志（保护机制4）

**文件位置**：`callbacks/core_pages_c/chat_input_area_c.py` 或相关回调文件

**实现方式**：在消息重新生成的回调中添加清理逻辑

**代码**：
```python
# 在 _handle_ai_regenerate 或 handle_message_operations 中添加
def handle_message_operations(ai_regenerate_clicks, user_regenerate_clicks, cancel_clicks, 
                             messages, current_session_id, send_btn_clicks):
    # ... 现有代码 ...
    
    # 处理AI消息重新生成
    if '"type":"ai-chat-x-regenerate"' in prop_id:
        id_part = prop_id.split('.')[0]
        id_dict = json.loads(id_part)
        target_message_id = id_dict['index']
        
        # 🔧 关键保护机制4：清理停止标志，允许重新播放
        # 需要在客户端JavaScript中执行，添加客户端回调或使用dcc.Store触发
        # 这里通过添加客户端JavaScript代码来处理
```

**客户端JavaScript实现**：
```javascript
// 在 chat.py 的 html.Script 块中添加
// 监听消息重新生成，清理停止标志
document.addEventListener('DOMContentLoaded', function() {
    // 监听消息重新生成按钮点击
    document.addEventListener('click', function(event) {
        const regenerateButton = event.target.closest('[id*="ai-chat-x-regenerate"]');
        if (regenerateButton) {
            // 从按钮ID中提取messageId
            let messageId = null;
            if (regenerateButton.id && typeof regenerateButton.id === 'object') {
                messageId = regenerateButton.id.index;
            } else {
                // 尝试解析ID字符串
                try {
                    const idStr = regenerateButton.id || regenerateButton.closest('[id]')?.id;
                    if (idStr) {
                        const idMatch = idStr.match(/ai-chat-x-regenerate.*?index.*?(\d+)/);
                        if (idMatch) {
                            messageId = idMatch[1];
                        }
                    }
                } catch (e) {
                    console.warn('无法解析重新生成按钮的messageId:', e);
                }
            }
            
            if (messageId) {
                // 清理停止标志，允许重新播放
                if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.clearStopFlag) {
                    window.voicePlayerEnhanced.clearStopFlag(`ai-message-${messageId}`);
                    window.controlledLog?.log('✅ 重新生成消息，清理停止标志:', messageId);
                }
            }
        }
    });
});
```

### 步骤4：添加客户端 JavaScript - 监听按钮点击和动态显示

**文件位置**：`views/core_pages/chat.py`（在`html.Script`块中添加）

#### 3.1 添加停止按钮点击监听
```javascript
// 🔧 新增：监听TTS停止按钮点击
document.addEventListener('click', function(event) {
    // 检查是否是停止按钮（包括按钮本身或其子元素）
    const stopButton = event.target.closest('[id*="ai-chat-x-stop-tts"]') || 
                       event.target.closest('.tts-stop-button');
    
    if (stopButton) {
        event.preventDefault();
        event.stopPropagation();
        
        // 从按钮ID中提取messageId
        let messageId = null;
        if (stopButton.id && typeof stopButton.id === 'object') {
            messageId = stopButton.id.index;
        } else {
            // 尝试从父元素获取
            const wrapper = stopButton.closest('[id*="tts-stop-button-wrapper"]');
            if (wrapper && wrapper.id && typeof wrapper.id === 'object') {
                messageId = wrapper.id.index;
            }
        }
        
        if (!messageId) {
            window.controlledLog?.log('⚠️ 无法获取messageId');
            return;
        }
        
        window.controlledLog?.log('🔊 TTS停止按钮被点击，messageId:', messageId);
        
        // 停止简单TTS播放
        if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.stopSimpleTTS) {
            window.voicePlayerEnhanced.stopSimpleTTS(messageId);
            window.controlledLog?.log('✅ TTS播放已停止');
        } else {
            console.warn('⚠️ 播放器或stopSimpleTTS方法不可用');
        }
    }
});
```

#### 3.2 添加按钮动态显示/隐藏逻辑
```javascript
// 🔧 新增：动态更新TTS停止按钮的显示/隐藏状态
function updateTtsStopButtons() {
    // 检查是否有TTS正在播放
    const isTtsPlaying = window.voicePlayerEnhanced && 
                         (window.voicePlayerEnhanced.isTtsPlaying || 
                          window.voicePlayerEnhanced.simplePlaying);
    
    // 检查simpleQueue中是否有待播放的音频
    const hasQueuedAudio = window.voicePlayerEnhanced && 
                          window.voicePlayerEnhanced.simpleQueue && 
                          window.voicePlayerEnhanced.simpleQueue.length > 0;
    
    // 获取所有消息ID及其对应的停止按钮包装器
    const allMessageIds = new Set();
    
    // 从simpleQueue中获取所有正在播放的消息ID
    if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.simpleQueue) {
        window.voicePlayerEnhanced.simpleQueue.forEach(item => {
            if (item.messageId) {
                allMessageIds.add(item.messageId);
            }
        });
    }
    
    // 从streamStates中获取所有正在播放的消息ID
    if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.streamStates) {
        window.voicePlayerEnhanced.streamStates.forEach((state, messageId) => {
            // 只显示录音聊天和文本聊天的消息（不包含voice_call）
            if (messageId && !messageId.includes('voice_call') && state.playingSources > 0) {
                allMessageIds.add(messageId);
            }
        });
    }
    
    // 获取所有停止按钮包装器
    const stopButtonWrappers = document.querySelectorAll('[id*="tts-stop-button-wrapper"]');
    
    stopButtonWrappers.forEach(wrapper => {
        // 从wrapper的ID中提取messageId
        let messageId = null;
        if (wrapper.id && typeof wrapper.id === 'object') {
            messageId = wrapper.id.index;
        }
        
        if (!messageId) {
            return;
        }
        
        // 检查该消息是否正在播放且未被停止
        const isThisMessagePlaying = allMessageIds.has(messageId) && 
                                    (!window.voicePlayerEnhanced.stoppedSimpleTTS || 
                                     !window.voicePlayerEnhanced.stoppedSimpleTTS.get(messageId));
        
        // 根据播放状态显示/隐藏按钮
        if (isThisMessagePlaying && (isTtsPlaying || hasQueuedAudio)) {
            wrapper.style.display = 'inline-block';
        } else {
            wrapper.style.display = 'none';
        }
    });
}

// 定期检查并更新按钮显示状态（每500ms检查一次）
setInterval(updateTtsStopButtons, 500);

// 监听播放状态变化，立即更新按钮显示
if (window.voicePlayerEnhanced) {
    // 监听simplePlaying状态变化
    const originalProcessSimpleQueue = window.voicePlayerEnhanced.processSimpleQueue;
    if (originalProcessSimpleQueue) {
        window.voicePlayerEnhanced.processSimpleQueue = function(...args) {
            const result = originalProcessSimpleQueue.apply(this, args);
            setTimeout(updateTtsStopButtons, 100);
            return result;
        };
    }
}
```

## 四、测试验证

### 4.1 功能测试
1. **文本聊天TTS停止**
   - 发送文本消息
   - 等待TTS开始播放
   - 点击停止按钮
   - 验证：音频立即停止，后续音频数据不播放

2. **录音聊天TTS停止**
   - 点击录音按钮
   - 等待TTS开始播放
   - 点击停止按钮
   - 验证：音频立即停止，后续音频数据不播放

3. **多消息场景**
   - 连续发送多条消息
   - 验证：只有正在播放的消息显示停止按钮
   - 点击停止按钮后，只有该消息停止，其他消息继续播放

### 4.2 边界情况测试
1. **WebSocket持续接收**
   - 停止后，验证后续音频数据被丢弃
   - 验证不会重新开始播放

2. **状态重置**
   - 停止后，验证按钮状态正确重置
   - 验证下次播放时按钮正确显示

## 六、总结

### 6.1 核心机制
1. **三层拦截机制**：确保被停止的消息不会播放
   - 入口拦截：`handleAudioStream`
   - 二次检查：`playSimpleTTS`
   - 播放前检查：`playSimpleAudioBuffer`

2. **停止标志跟踪**：使用Map跟踪每个消息的停止状态
   - 设置：`stopSimpleTTS`方法中
   - 清理：`handleSynthesisComplete`、超时清理、手动清理

3. **动态按钮显示**：根据播放状态动态显示/隐藏按钮
   - 每500ms检查一次播放状态
   - 根据消息ID匹配显示对应按钮

### 6.2 关键技术点
- **入口拦截**：在`handleAudioStream`中检查停止标志
- **二次检查**：在`playSimpleTTS`中再次检查
- **源跟踪**：保存`simpleCurrentSource`以便停止
- **队列清理**：停止时从队列中移除被停止的消息
- **队列过滤**：在处理队列时过滤已停止的消息
- **状态重置**：停止后正确重置播放标志和按钮状态

### 6.3 关键保护机制（必须实现）
1. **超时清理机制**：5分钟后自动清理停止标志，防止永久阻止
2. **队列过滤机制**：在处理队列时过滤已停止的消息
3. **合成完成清理**：TTS合成完成时清理停止标志
4. **重新生成清理**：消息重新生成时清理停止标志

### 6.4 注意事项
- **停止标志管理**：必须确保停止标志在合适的时机被清理
- **多消息场景**：确保只停止指定消息，不影响其他消息
- **按钮状态**：确保按钮状态与播放状态同步
- **状态重置**：确保停止后正确重置所有相关状态

### 6.5 风险评估
- **功能影响**：✅ 低风险 - 不影响现有功能
- **按钮状态**：✅ 低风险 - 复用现有机制
- **代码稳定性**：⚠️ 中风险 - 需要补充保护机制（已补充）
- **用户体验**：🟢 低风险 - 提供新功能，体验良好

**结论**：✅ **方案可行，已补充所有关键保护机制**

