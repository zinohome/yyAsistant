/**
 * 语音WebSocket管理器
 * 专门处理与yychat后端的语音WebSocket通信
 */

class VoiceWebSocketManager {
    constructor() {
        this.ws = null;
        this.clientId = null;
        this.sessionId = null;  // 当前会话ID (conversation_id)
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 1000;
        this.heartbeatInterval = null;
        this.messageHandlers = new Map();
        this.connectionHandlers = [];
        this.disconnectionHandlers = [];
        // 预注册心跳回应为no-op，避免未注册报错
        this.messageHandlers.set('heartbeat_response', () => {});
        
        // 从配置获取WebSocket URL，并附带持久化client_id
        this.wsUrlBase = window.voiceConfig?.WS_URL || 'ws://192.168.66.209:9800/ws/chat';
        this.persistentClientId = this.ensurePersistentClientId();
        this.wsUrl = this.appendClientId(this.wsUrlBase, this.persistentClientId);
        
        // 初始化全局状态
        this.initGlobalState();
    }
    
    /**
     * 确保存在持久化client_id（localStorage）
     */
    ensurePersistentClientId() {
        try {
            const key = 'voiceClientId';
            let cid = localStorage.getItem(key);
            if (!cid) {
                cid = self.crypto?.randomUUID ? self.crypto.randomUUID() : (Date.now().toString(36) + Math.random().toString(36).slice(2));
                localStorage.setItem(key, cid);
            }
            // 初始化到全局状态，便于SSE兜底读取
            if (!window.voiceChatState) {
                window.voiceChatState = {};
            }
            window.voiceChatState.clientId = window.voiceChatState.clientId || cid;
            return cid;
        } catch (e) {
            return Date.now().toString(36) + Math.random().toString(36).slice(2);
        }
    }
    
    /**
     * 追加client_id到WS URL
     */
    appendClientId(url, clientId) {
        try {
            const hasQuery = url.includes('?');
            const sep = hasQuery ? '&' : '?';
            return `${url}${sep}client_id=${encodeURIComponent(clientId)}`;
        } catch (_) {
            return url;
        }
    }
    
    /**
     * 初始化全局状态管理
     */
    initGlobalState() {
        // 创建全局状态对象
        window.voiceChatState = {
            clientId: null,
            sessionId: null,
            isConnected: false,
            activeMessageId: null
        };
        
        // 监听会话切换事件
        document.addEventListener('conversationSwitched', (event) => {
            this.updateSessionId(event.detail.conversationId);
        });
    }
    
    /**
     * 更新会话ID
     */
    updateSessionId(conversationId) {
        this.sessionId = conversationId;
        window.voiceChatState.sessionId = conversationId;
        console.log('WebSocket管理器更新会话ID:', conversationId);
    }
    
    /**
     * 建立WebSocket连接
     */
    async connect() {
        try {
            console.log('正在连接语音WebSocket:', this.wsUrl);
            
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = (event) => {
                console.log('语音WebSocket连接已建立');
                // 新连接建立时，清空旧的 clientId，等待服务端下发新的 connection_established 进行绑定
                this.clientId = null;
                window.voiceChatState.clientId = null;
                // 尝试从页面当前会话控件读取会话ID，避免 session 校验期望为 null
                try {
                    const el = document.getElementById('ai-chat-x-current-session-id');
                    const sid = (el && (el.value || el.textContent)) ? (el.value || el.textContent) : null;
                    if (sid) {
                        this.updateSessionId(sid);
                    }
                } catch (_) {}
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.notifyConnectionHandlers(true);
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.ws.onclose = (event) => {
                console.log('语音WebSocket连接已关闭:', event.code, event.reason);
                // 连接关闭时也清理 clientId，避免用旧 id 校验新连接的首条消息
                this.clientId = null;
                window.voiceChatState.clientId = null;
                this.isConnected = false;
                this.stopHeartbeat();
                this.notifyDisconnectionHandlers();
                
                // 自动重连
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('语音WebSocket连接错误:', error);
                this.notifyConnectionHandlers(false);
            };
            
            return true;
        } catch (error) {
            console.error('语音WebSocket连接失败:', error);
            return false;
        }
    }
    
    /**
     * 断开WebSocket连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.stopHeartbeat();
    }
    
    /**
     * 发送消息
     */
    sendMessage(message) {
        if (!this.isConnected || !this.ws) {
            console.error('WebSocket未连接，无法发送消息');
            return false;
        }
        
        try {
            const messageStr = JSON.stringify(message);
            this.ws.send(messageStr);
            console.log('发送语音消息:', message.type);
            return true;
        } catch (error) {
            console.error('发送消息失败:', error);
            return false;
        }
    }
    
    /**
     * 发送音频输入消息
     */
    sendAudioInput(audioData, options = {}) {
        const message = {
            type: 'audio_input',
            audio_data: this.encodeAudioData(audioData),
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId,
            ...options
        };
        return this.sendMessage(message);
    }
    
    /**
     * 发送音频流消息
     */
    sendAudioStream(audioChunk, options = {}) {
        const message = {
            type: 'audio_stream',
            audio_data: this.encodeAudioData(audioChunk),
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId,
            ...options
        };
        return this.sendMessage(message);
    }
    
    /**
     * 发送语音命令
     */
    sendVoiceCommand(command, options = {}) {
        const message = {
            type: 'voice_command',
            command: command,
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId,
            ...options
        };
        return this.sendMessage(message);
    }
    
    /**
     * 查询状态
     */
    sendStatusQuery() {
        const message = {
            type: 'status_query',
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId
        };
        return this.sendMessage(message);
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('收到语音消息:', message.type);

            // 如果首次收到带有client_id的消息，先建立绑定，再进行校验，避免"expected: null"误丢弃
            if (message.client_id && !window.voiceChatState.clientId) {
                this.clientId = message.client_id;
                window.voiceChatState.clientId = this.clientId;
                window.voiceChatState.isConnected = this.isConnected;
                console.log('首次绑定client_id:', this.clientId);
                if (window.dash_clientside && window.dash_clientside.set_props) {
                    window.dash_clientside.set_props('voice-websocket-connection', {
                        data: {
                            connected: true,
                            client_id: this.clientId,
                            timestamp: Date.now()
                        }
                    });
                    // 若当前正处于语音触发流程，但之前因缺少 client_id 未能开启 TTS，这里补写一次开关，促使后端拿到client_id
                    try {
                        window.dash_clientside.set_props('voice-enable-voice', {
                            data: {
                                enable: true,
                                client_id: this.clientId,
                                ts: Date.now()
                            }
                        });
                    } catch (e) {
                        console.warn('设置voice-enable-voice失败（可忽略）:', e);
                    }

                    // 额外重试：短时间内重复写入，避免首写入因渲染时序未生效
                    try {
                        let tries = 0;
                        const maxTries = 5;
                        const timer = setInterval(() => {
                            tries += 1;
                            try {
                                window.dash_clientside.set_props('voice-websocket-connection', {
                                    data: {
                                        connected: true,
                                        client_id: this.clientId,
                                        timestamp: Date.now()
                                    }
                                });
                            } catch (_) {}
                            if (tries >= maxTries) {
                                clearInterval(timer);
                            }
                        }, 200);
                    } catch (_) {}
                }
            }

            // 消息验证 - 防串台机制
            if (!this.validateMessage(message)) {
                console.warn('消息验证失败，丢弃消息:', message);
                return;
            }

            // 更新客户端ID（非首次场景）
            if (message.client_id && this.clientId !== message.client_id) {
                this.clientId = message.client_id;
                window.voiceChatState.clientId = this.clientId;
                console.log('更新client_id:', this.clientId);
            }
            
            // 调用对应的处理器
            const handler = this.messageHandlers.get(message.type);
            if (handler) {
                console.log('调用消息处理器:', message.type);
                try {
                    handler(message);
                } catch (error) {
                    console.error('消息处理器执行失败:', message.type, error);
                }
            } else {
                console.warn('未找到消息处理器:', message.type);
            }
        } catch (error) {
            console.error('解析消息失败:', error);
        }
    }
    
    /**
     * 验证消息是否属于当前用户 - 防串台机制
     */
    validateMessage(message) {
        const { client_id, session_id } = message;
        const state = window.voiceChatState;
        
        // 检查client_id
        if (client_id && client_id !== state.clientId) {
            console.warn('消息client_id不匹配，丢弃:', {
                received: client_id,
                expected: state.clientId
            });
            return false;
        }
        
        // 检查session_id (conversation_id)
        // 仅当本地已记录期望的 sessionId 时才严格校验；否则先放行以完成首次绑定
        if (state.sessionId && session_id && session_id !== state.sessionId) {
            console.warn('消息session_id不匹配，丢弃:', {
                received: session_id,
                expected: state.sessionId
            });
            return false;
        }
        
        return true;
    }
    
    /**
     * 注册消息处理器
     */
    registerMessageHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
        console.log('注册消息处理器:', messageType);
    }
    
    /**
     * 注册连接处理器
     */
    registerConnectionHandler(handler) {
        this.connectionHandlers.push(handler);
    }
    
    /**
     * 注册断开连接处理器
     */
    registerDisconnectionHandler(handler) {
        this.disconnectionHandlers.push(handler);
    }
    
    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.sendMessage({
                    type: 'heartbeat',
                    timestamp: Date.now() / 1000,
                    client_id: this.clientId
                });
            }
        }, 30000); // 30秒心跳
    }
    
    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
        console.log(`将在 ${delay}ms 后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    /**
     * 通知连接处理器
     */
    notifyConnectionHandlers(success) {
        this.connectionHandlers.forEach(handler => {
            try {
                handler(success);
            } catch (error) {
                console.error('连接处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 通知断开连接处理器
     */
    notifyDisconnectionHandlers() {
        this.disconnectionHandlers.forEach(handler => {
            try {
                handler();
            } catch (error) {
                console.error('断开连接处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 编码音频数据为base64
     */
    encodeAudioData(audioData) {
        if (audioData instanceof Blob) {
            // 对于Blob对象，需要异步处理
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.readAsDataURL(audioData);
            });
        } else if (audioData instanceof ArrayBuffer) {
            // 对于ArrayBuffer，直接转换
            const bytes = new Uint8Array(audioData);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        } else {
            // 假设已经是base64字符串
            return audioData;
        }
    }
    
    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            clientId: this.clientId,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
    
    /**
     * 获取WebSocket连接对象
     */
    getConnection() {
        if (!this.isConnected || !this.ws) {
            console.warn('WebSocket未连接，尝试连接...');
            this.connect();
            return null;
        }
        return this.ws;
    }
}

// 创建全局实例
window.voiceWebSocketManager = new VoiceWebSocketManager();
