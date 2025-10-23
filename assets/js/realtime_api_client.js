/**
 * OpenAI Realtime API客户端
 * 处理与OpenAI Realtime API的直接连接
 */

class RealtimeAPIClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.token = null;
        this.model = "gpt-4o-realtime-preview-2024-10-01";
        this.url = null;
        this.eventHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 1000; // 1秒
    }
    
    /**
     * 连接到OpenAI Realtime API
     */
    async connect() {
        try {
            console.log('开始连接OpenAI Realtime API...');
            
            // 1. 从后端获取token
            await this.fetchToken();
            
            // 2. 建立WebSocket连接
            await this.establishConnection();
            
            this.isConnected = true;
            console.log('OpenAI Realtime API连接成功');
            
            // 触发连接成功事件
            this.emit('connected');
            
        } catch (error) {
            console.error('连接OpenAI Realtime API失败:', error);
            this.emit('error', error);
            throw error;
        }
    }
    
    /**
     * 从后端获取token
     */
    async fetchToken() {
        try {
            const response = await fetch('/v1/realtime/token', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`获取token失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`获取token失败: ${data.error || '未知错误'}`);
            }
            
            this.token = data.data.token;
            this.url = data.data.url;
            this.model = data.data.model;
            
            console.log('Token获取成功');
            
        } catch (error) {
            console.error('获取token失败:', error);
            throw error;
        }
    }
    
    /**
     * 建立WebSocket连接
     */
    async establishConnection() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url, {
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'OpenAI-Beta': 'realtime=v1'
                    }
                });
                
                this.setupEventHandlers(resolve, reject);
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * 设置WebSocket事件处理器
     */
    setupEventHandlers(resolve, reject) {
        this.ws.onopen = () => {
            console.log('WebSocket连接已建立');
            this.reconnectAttempts = 0;
            resolve();
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('处理WebSocket消息失败:', error);
                this.emit('error', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket错误:', error);
            this.emit('error', error);
        };
        
        this.ws.onclose = (event) => {
            console.log('WebSocket连接已关闭:', event.code, event.reason);
            this.isConnected = false;
            this.emit('disconnected', event);
            
            // 自动重连
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect();
            }
        };
    }
    
    /**
     * 处理WebSocket消息
     */
    handleMessage(data) {
        console.log('收到Realtime API消息:', data);
        
        switch (data.type) {
            case 'session.created':
                this.emit('session_created', data);
                break;
            case 'session.updated':
                this.emit('session_updated', data);
                break;
            case 'conversation.item.input_audio_buffer.committed':
                this.emit('audio_committed', data);
                break;
            case 'conversation.item.input_audio_buffer.speech_started':
                this.emit('speech_started', data);
                break;
            case 'conversation.item.input_audio_buffer.speech_stopped':
                this.emit('speech_stopped', data);
                break;
            case 'conversation.item.output_audio_buffer.speech_started':
                this.emit('ai_speech_started', data);
                break;
            case 'conversation.item.output_audio_buffer.speech_stopped':
                this.emit('ai_speech_stopped', data);
                break;
            case 'conversation.item.output_audio_buffer.committed':
                this.emit('ai_audio_committed', data);
                break;
            case 'conversation.item.output_audio_buffer.delta':
                this.emit('ai_audio_delta', data);
                break;
            case 'conversation.item.output_text.delta':
                this.emit('ai_text_delta', data);
                break;
            case 'conversation.item.output_text.committed':
                this.emit('ai_text_committed', data);
                break;
            case 'conversation.item.tool_call.created':
                this.emit('tool_call_created', data);
                break;
            case 'conversation.item.tool_call.updated':
                this.emit('tool_call_updated', data);
                break;
            case 'conversation.item.tool_call.completed':
                this.emit('tool_call_completed', data);
                break;
            case 'conversation.item.tool_call.failed':
                this.emit('tool_call_failed', data);
                break;
            case 'error':
                this.emit('api_error', data);
                break;
            default:
                console.log('未知消息类型:', data.type);
                this.emit('unknown_message', data);
        }
    }
    
    /**
     * 发送消息到Realtime API
     */
    sendMessage(message) {
        if (!this.isConnected || !this.ws) {
            throw new Error('WebSocket未连接');
        }
        
        try {
            this.ws.send(JSON.stringify(message));
            console.log('发送消息到Realtime API:', message);
        } catch (error) {
            console.error('发送消息失败:', error);
            throw error;
        }
    }
    
    /**
     * 更新会话配置
     */
    updateSession(config) {
        const message = {
            type: 'session.update',
            session: config
        };
        
        this.sendMessage(message);
    }
    
    /**
     * 发送音频数据
     */
    sendAudio(audioData) {
        const message = {
            type: 'conversation.item.input_audio_buffer.append',
            audio: audioData
        };
        
        this.sendMessage(message);
    }
    
    /**
     * 提交音频缓冲区
     */
    commitAudioBuffer() {
        const message = {
            type: 'conversation.item.input_audio_buffer.commit'
        };
        
        this.sendMessage(message);
    }
    
    /**
     * 开始语音输入
     */
    startSpeech() {
        const message = {
            type: 'conversation.item.input_audio_buffer.speech_started'
        };
        
        this.sendMessage(message);
    }
    
    /**
     * 停止语音输入
     */
    stopSpeech() {
        const message = {
            type: 'conversation.item.input_audio_buffer.speech_stopped'
        };
        
        this.sendMessage(message);
    }
    
    /**
     * 断开连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        console.log('已断开Realtime API连接');
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * this.reconnectAttempts;
        
        console.log(`安排重连，延迟 ${delay}ms (尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect().catch(error => {
                console.error('重连失败:', error);
            });
        }, delay);
    }
    
    /**
     * 获取API密钥
     */
    getApiKey() {
        // 从全局配置或环境变量获取API密钥
        return window.appConfig?.getApiKey() || window.voiceConfig?.API_KEY || 'yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4';
    }
    
    /**
     * 事件监听器
     */
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    /**
     * 移除事件监听器
     */
    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }
    
    /**
     * 触发事件
     */
    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`事件处理器错误 (${event}):`, error);
                }
            });
        }
    }
}

// 导出类
window.RealtimeAPIClient = RealtimeAPIClient;
