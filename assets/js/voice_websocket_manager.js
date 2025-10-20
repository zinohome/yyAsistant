/**
 * 语音WebSocket管理器
 * 专门处理与yychat后端的语音WebSocket通信
 */

/**
 * 语音WebSocket管理器
 * 使用隐藏div和Dash clientside callback机制来更新Store
 */

class VoiceWebSocketManager {
    constructor() {
        this.ws = null;
        this.clientId = null;
        this.sessionId = null;  // 当前会话ID (conversation_id)
        this.isConnected = false;
        this.isConnecting = false;  // 添加连接中标志
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 1000;
        this.heartbeatInterval = null;
        this.messageHandlers = new Map();
        this.connectionHandlers = [];
        this.disconnectionHandlers = [];
        // 预注册心跳回应为no-op，避免未注册报错
        this.messageHandlers.set('heartbeat_response', () => {});
        // 预注册音频消息处理器占位，避免未注册时报错
        this.messageHandlers.set('audio_stream', () => {});
        this.messageHandlers.set('voice_response', () => {});
        this.messageHandlers.set('synthesis_complete', () => {});
        
        // 从配置获取WebSocket URL，并附带持久化client_id
        this.wsUrlBase = window.voiceConfig?.WS_URL || 'ws://192.168.32.156:9800/ws/chat';
        this.persistentClientId = this.ensurePersistentClientId();
        this.wsUrl = this.appendClientId(this.wsUrlBase, this.persistentClientId);
        
        // 初始化全局状态
        this.initGlobalState();

        // 移除复杂的队列机制，直接使用简单的更新方式
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

    // 移除有问题的updateDashStore方法，完全使用事件机制

    // 移除复杂的队列机制
    
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
        // 如果正在连接中，直接返回
        if (this.isConnecting) {
            console.log('WebSocket正在连接中，跳过重复连接');
            return Promise.resolve();
        }
        
        this.isConnecting = true;
        return new Promise((resolve, reject) => {
            try {
                console.log('正在连接语音WebSocket:', this.wsUrl);
                
                this.ws = new WebSocket(this.wsUrl);
                
                this.ws.onopen = (event) => {
                    console.log('语音WebSocket连接已建立');
                    this.isConnected = true;
                    this.isConnecting = false;  // 重置连接中标志
                    // 新连接建立时，清空旧的 clientId，等待服务端下发新的 connection_established 进行绑定
                    this.clientId = null;
                    window.voiceChatState.clientId = null;
                    
                    // 使用事件机制更新连接状态
                    try {
                        const event = new CustomEvent('voiceWebSocketConnecting', {
                            detail: { connected: true, client_id: null, timestamp: Date.now() }
                        });
                        document.dispatchEvent(event);
                        console.log('连接时使用事件机制更新状态');
                    } catch (e) {
                        console.warn('连接时事件机制失败:', e);
                    }
                    // 清理本地存储的旧 client_id，强制重新生成
                    try {
                        localStorage.removeItem('voiceClientId');
                    } catch (_) {}
                    // 重新生成持久化 client_id
                    this.persistentClientId = this.ensurePersistentClientId();
                    this.wsUrl = this.appendClientId(this.wsUrlBase, this.persistentClientId);
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
                    resolve(true);
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
                    this.isConnecting = false;  // 重置连接中标志
                    this.stopHeartbeat();
                    this.notifyDisconnectionHandlers();
                    
                    // 自动重连
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.scheduleReconnect();
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('语音WebSocket连接错误:', error);
                    this.isConnecting = false;  // 重置连接中标志
                    this.notifyConnectionHandlers(false);
                    reject(error);
                };
                
            } catch (error) {
                console.error('语音WebSocket连接失败:', error);
                this.isConnecting = false;  // 重置连接中标志
                reject(error);
            }
        });
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
        this.isConnecting = false;  // 重置连接中标志
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
            // 注释掉心跳消息的日志
            if (message.type !== 'heartbeat') {
                console.log('发送语音消息:', message.type);
            }
            return true;
        } catch (error) {
            console.error('发送消息失败:', error);
            return false;
        }
    }
    
    /**
     * 发送音频输入消息
     */
    async sendAudioInput(audioData, options = {}) {
        try {
            const encodedAudio = await this.encodeAudioData(audioData);
            const message = {
                type: 'audio_input',
                // 兼容后端旧STT管线字段：使用 audio_base64
                audio_base64: encodedAudio,
                timestamp: Date.now() / 1000,
                client_id: this.clientId,
                session_id: this.sessionId,
                ...options
            };
            return this.sendMessage(message);
        } catch (error) {
            console.error('编码音频数据失败:', error);
            return false;
        }
    }
    
    /**
     * 发送音频流消息
     */
    sendAudioStream(audioChunk, options = {}) {
        const message = {
            type: 'audio_stream',
            // 兼容后端旧字段：使用 audio_base64
            audio_base64: this.encodeAudioData(audioChunk),
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
            // 注释掉心跳消息的日志
            if (message.type !== 'heartbeat_response') {
                console.log('收到语音消息:', message.type);
            }

            // 仅在 connection_established 时绑定 client_id，提高安全性
            if (message.type === 'connection_established' && message.client_id) {
                this.clientId = message.client_id;
                if (!window.voiceChatState) {
                    window.voiceChatState = {};
                }
                window.voiceChatState.clientId = this.clientId;
                window.voiceChatState.isConnected = this.isConnected;
                console.log('首次绑定client_id:', this.clientId);
                
                // 立即写入 Dash Store，便于 SSE 侧携带一致的 client_id
                const connectionData = { connected: true, client_id: this.clientId, timestamp: Date.now() };
                const enableVoiceData = { enable: true, client_id: this.clientId, ts: Date.now() };
                
            // 使用全局变量存储client_id，避免时机问题
            window.voiceClientId = this.clientId;
            window.voiceWebSocketConnected = true;
            console.log('已设置全局client_id:', this.clientId);
            
            // 添加全局函数来获取client_id
            window.getVoiceClientId = () => {
                return window.voiceClientId || null;
            };
            
            // 添加一个方法来获取当前的client_id
            this.getClientId = () => {
                return this.clientId || window.voiceClientId;
            };
            
            // 使用正确的dash_clientside.set_props语法更新Store
            const updateDashStore = () => {
                try {
                    // 只在/core/chat页面更新WebSocket Store
                    const currentPath = window.location.pathname;
                    const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                    
                    if (!isChatPage) {
                        console.log('当前页面不需要更新WebSocket Store:', currentPath);
                        return;
                    }
                    
                    if (window.dash_clientside && window.dash_clientside.set_props) {
                        console.log('使用dash_clientside.set_props更新Store，clientId:', this.clientId);
                        
                        try {
                            // 更新WebSocket连接状态 - 使用正确的语法
                            window.dash_clientside.set_props('voice-websocket-connection', {
                                data: { 
                                    connected: true, 
                                    client_id: this.clientId, 
                                    timestamp: Date.now() 
                                }
                            });
                            console.log('voice-websocket-connection 更新成功');
                            
                            // 更新语音开关状态 - 使用正确的语法
                            window.dash_clientside.set_props('voice-enable-voice', {
                                data: { 
                                    enable: true, 
                                    client_id: this.clientId, 
                                    ts: Date.now() 
                                }
                            });
                            console.log('voice-enable-voice 更新成功');
                        } catch (setPropsError) {
                            console.error('set_props调用失败:', setPropsError);
                            // 延迟重试
                            setTimeout(updateDashStore, 200);
                        }
                    } else {
                        console.log('dash_clientside.set_props 不可用，延迟重试');
                        setTimeout(updateDashStore, 200);
                    }
                } catch (e) {
                    console.error('更新Dash Store失败:', e);
                    // 延迟重试
                    setTimeout(updateDashStore, 200);
                }
            };
            
            // 延迟执行，确保Dash完全初始化
            setTimeout(updateDashStore, 500);
            }

            // 消息验证 - 防串台机制（在完成绑定之后再校验）
            if (!this.validateMessage(message)) {
                console.warn('消息验证失败，丢弃消息:', message);
                return;
            }

            // 此处无需再次更新client_id，上面已完成统一绑定
            
            // 调用对应的处理器
            const handler = this.messageHandlers.get(message.type);
            if (handler) {
                // 注释掉心跳消息处理器的日志
                if (message.type !== 'heartbeat_response') {
                    console.log('调用消息处理器:', message.type);
                }
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
        // 如果已连接，直接返回连接
        if (this.isConnected && this.ws) {
            return this.ws;
        }
        
        // 如果正在连接中，等待连接完成
        if (this.isConnecting) {
            console.log('WebSocket正在连接中，等待连接完成...');
            return null;
        }
        
        // 如果未连接，尝试连接（只允许一次）
        if (!this.isConnected && !this.isConnecting) {
            console.warn('WebSocket未连接，尝试连接...');
            this.connect();
        }
        
        return null; // 连接中或未连接时返回null
    }
    
    /**
     * 等待连接建立（用于组件初始化）
     */
    async waitForConnection(maxWaitTime = 5000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < maxWaitTime) {
            if (this.isConnected && this.ws) {
                return this.ws;
            }
            if (this.isConnecting) {
                // 等待连接完成
                await new Promise(resolve => setTimeout(resolve, 100));
                continue;
            }
            // 如果既未连接也不在连接中，尝试连接
            if (!this.isConnected && !this.isConnecting) {
                this.connect();
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.warn('等待WebSocket连接超时');
        return null;
    }
}

// 创建全局实例
window.voiceWebSocketManager = new VoiceWebSocketManager();
