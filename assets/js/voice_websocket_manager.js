/**
 * 语音WebSocket管理器
 * 专门处理与yychat后端的语音WebSocket通信
 */

class VoiceWebSocketManager {
    constructor() {
        this.ws = null;
        this.clientId = null;
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
        
        // 从配置获取WebSocket URL
        this.wsUrl = window.voiceConfig?.WS_URL || 'ws://192.168.66.209:9800/ws/chat';
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
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.notifyConnectionHandlers(true);
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
                try {
                    const data = JSON.parse(event.data);
                    if (data && data.type === 'connection_established' && data.client_id) {
                        this.clientId = data.client_id;
                        // 将client_id同步到Dash Store，供SSE触发时使用
                        if (window.dash_clientside && window.dash_clientside.set_props) {
                            window.dash_clientside.set_props('voice-websocket-connection', {
                                data: {
                                    connected: true,
                                    client_id: this.clientId,
                                    timestamp: Date.now()
                                }
                            });
                        }
                    }
                } catch (e) {
                    // 忽略非JSON消息
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('语音WebSocket连接已关闭:', event.code, event.reason);
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
            client_id: this.clientId
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
            
            // 更新客户端ID
            if (message.client_id) {
                this.clientId = message.client_id;
            }
            
            // 调用对应的处理器
            const handler = this.messageHandlers.get(message.type);
            if (handler) {
                handler(message);
            } else {
                console.warn('未找到消息处理器:', message.type);
            }
        } catch (error) {
            console.error('解析消息失败:', error);
        }
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
