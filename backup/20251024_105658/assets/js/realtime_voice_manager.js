/**
 * 实时语音管理器
 * 整合所有实时语音功能的主控制器
 */

class RealtimeVoiceManager {
    constructor() {
        // 核心组件
        this.apiClient = new RealtimeAPIClient();
        this.audioProcessor = new RealtimeAudioProcessor();
        this.adapterClient = new RealtimeAdapterClient();
        
        // 状态管理
        this.isActive = false;
        this.currentState = 'idle'; // idle, connecting, listening, processing, speaking, error
        this.conversationId = null;
        this.personalityId = null;
        this.sessionConfig = null;
        
        // 事件处理器
        this.eventHandlers = {};
        
        // 配置
        this.config = {
            backendUrl: window.voiceConfig?.BACKEND_URL || 'http://localhost:9800',
            apiKey: window.voiceConfig?.API_KEY || 'yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4',
            personalityId: window.voiceConfig?.PERSONALITY_ID || 'default',
            conversationId: null
        };
        
        this.initialize();
    }
    
    /**
     * 初始化管理器
     */
    initialize() {
        console.log('初始化实时语音管理器...');
        
        // 设置适配器客户端配置
        this.adapterClient.setBackendUrl(this.config.backendUrl);
        this.adapterClient.setApiKey(this.config.apiKey);
        
        // 设置音频处理器回调
        this.setupAudioCallbacks();
        
        // 设置API客户端回调
        this.setupAPICallbacks();
        
        console.log('实时语音管理器初始化完成');
    }
    
    /**
     * 设置音频处理器回调
     */
    setupAudioCallbacks() {
        // 音频可视化回调
        this.audioProcessor.setVisualizationCallback((audioLevel, dataArray) => {
            this.updateAudioVisualization(audioLevel, dataArray);
        });
        
        // 语音检测回调
        this.audioProcessor.setSpeechDetectionCallback((event) => {
            this.handleSpeechDetection(event);
        });
    }
    
    /**
     * 设置API客户端回调
     */
    setupAPICallbacks() {
        // 连接事件
        this.apiClient.on('connected', () => {
            console.log('Realtime API连接成功');
            this.updateState('listening');
        });
        
        this.apiClient.on('disconnected', () => {
            console.log('Realtime API连接断开');
            this.updateState('idle');
        });
        
        this.apiClient.on('error', (error) => {
            console.error('Realtime API错误:', error);
            this.updateState('error');
            this.emit('error', error);
        });
        
        // 语音事件
        this.apiClient.on('speech_started', () => {
            console.log('用户开始说话');
            this.updateState('listening');
        });
        
        this.apiClient.on('speech_stopped', () => {
            console.log('用户停止说话');
            this.updateState('processing');
        });
        
        this.apiClient.on('ai_speech_started', () => {
            console.log('AI开始说话');
            this.updateState('speaking');
        });
        
        this.apiClient.on('ai_speech_stopped', () => {
            console.log('AI停止说话');
            this.updateState('listening');
        });
        
        // 文本事件
        this.apiClient.on('ai_text_delta', (data) => {
            this.handleAITextDelta(data);
        });
        
        this.apiClient.on('ai_text_committed', (data) => {
            this.handleAITextCommitted(data);
        });
        
        // 工具调用事件
        this.apiClient.on('tool_call_created', (data) => {
            this.handleToolCallCreated(data);
        });
        
        this.apiClient.on('tool_call_completed', (data) => {
            this.handleToolCallCompleted(data);
        });
    }
    
    /**
     * 启动实时语音对话
     */
    async start() {
        try {
            console.log('启动实时语音对话...');
            
            this.updateState('connecting');
            
            // 1. 生成会话ID
            this.conversationId = this.generateConversationId();
            
            // 2. 创建会话
            await this.createSession();
            
            // 3. 连接Realtime API
            await this.apiClient.connect();
            
            // 4. 启动音频捕获
            await this.audioProcessor.startCapture();
            
            // 5. 配置会话
            await this.configureSession();
            
            this.isActive = true;
            this.updateState('listening');
            
            console.log('实时语音对话已启动');
            this.emit('started');
            
        } catch (error) {
            console.error('启动实时语音对话失败:', error);
            this.updateState('error');
            this.emit('error', error);
            throw error;
        }
    }
    
    /**
     * 停止实时语音对话
     */
    async stop() {
        try {
            console.log('停止实时语音对话...');
            
            this.updateState('connecting');
            
            // 1. 停止音频捕获
            this.audioProcessor.stopCapture();
            
            // 2. 断开API连接
            this.apiClient.disconnect();
            
            this.isActive = false;
            this.updateState('idle');
            
            console.log('实时语音对话已停止');
            this.emit('stopped');
            
        } catch (error) {
            console.error('停止实时语音对话失败:', error);
            this.updateState('error');
            this.emit('error', error);
            throw error;
        }
    }
    
    /**
     * 创建会话
     */
    async createSession() {
        try {
            const sessionData = await this.adapterClient.createSession(
                this.conversationId,
                this.personalityId || this.config.personalityId,
                this.sessionConfig
            );
            
            console.log('会话创建成功:', sessionData);
            return sessionData;
            
        } catch (error) {
            console.error('创建会话失败:', error);
            throw error;
        }
    }
    
    /**
     * 配置会话
     */
    async configureSession() {
        try {
            // 获取人格配置
            const personality = await this.adapterClient.getPersonality(
                this.personalityId || this.config.personalityId
            );
            
            // 获取工具列表
            const tools = await this.adapterClient.getTools(
                this.personalityId || this.config.personalityId
            );
            
            // 更新会话配置
            const sessionConfig = {
                instructions: personality.instructions,
                voice: personality.voice,
                speed: personality.speed,
                modalities: personality.modalities,
                tools: tools
            };
            
            this.apiClient.updateSession(sessionConfig);
            
            console.log('会话配置完成');
            
        } catch (error) {
            console.error('配置会话失败:', error);
            throw error;
        }
    }
    
    /**
     * 处理语音检测
     */
    handleSpeechDetection(event) {
        if (event === 'start') {
            this.apiClient.startSpeech();
        } else if (event === 'stop') {
            this.apiClient.stopSpeech();
            this.apiClient.commitAudioBuffer();
        }
    }
    
    /**
     * 处理AI文本增量
     */
    handleAITextDelta(data) {
        console.log('AI文本增量:', data);
        this.emit('ai_text_delta', data);
    }
    
    /**
     * 处理AI文本提交
     */
    handleAITextCommitted(data) {
        console.log('AI文本提交:', data);
        this.emit('ai_text_committed', data);
        
        // 保存到记忆
        if (this.conversationId && data.text) {
            this.saveToMemory(data.text);
        }
    }
    
    /**
     * 处理工具调用创建
     */
    handleToolCallCreated(data) {
        console.log('工具调用创建:', data);
        this.emit('tool_call_created', data);
    }
    
    /**
     * 处理工具调用完成
     */
    handleToolCallCompleted(data) {
        console.log('工具调用完成:', data);
        this.emit('tool_call_completed', data);
    }
    
    /**
     * 更新音频可视化
     */
    updateAudioVisualization(audioLevel, dataArray) {
        this.emit('audio_visualization', { audioLevel, dataArray });
    }
    
    /**
     * 更新状态
     */
    updateState(newState) {
        if (this.currentState !== newState) {
            const oldState = this.currentState;
            this.currentState = newState;
            
            console.log(`状态变更: ${oldState} -> ${newState}`);
            this.emit('state_changed', { oldState, newState });
            this.updateUI();
        }
    }
    
    /**
     * 更新UI
     */
    updateUI() {
        // 更新状态指示器
        this.updateStatusIndicator();
        
        // 更新按钮状态
        this.updateButtonStates();
        
        // 更新可视化
        this.updateVisualization();
    }
    
    /**
     * 更新状态指示器
     */
    updateStatusIndicator() {
        const statusElement = document.getElementById('realtime-voice-status');
        if (!statusElement) return;
        
        const statusText = this.getStatusText();
        const statusColor = this.getStatusColor();
        
        statusElement.innerHTML = `
            <span class="ant-badge ant-badge-status ant-badge-status-${statusColor}">
                <span class="ant-badge-status-dot ant-badge-status-dot-${statusColor}"></span>
                <span>${statusText}</span>
            </span>
            <span style="margin-left: 10px;">实时语音对话模式</span>
        `;
    }
    
    /**
     * 获取状态文本
     */
    getStatusText() {
        const statusMap = {
            'idle': '等待开始',
            'connecting': '正在连接...',
            'listening': '正在监听',
            'processing': '处理中...',
            'speaking': 'AI说话中',
            'error': '连接错误'
        };
        
        return statusMap[this.currentState] || '未知状态';
    }
    
    /**
     * 获取状态颜色
     */
    getStatusColor() {
        const colorMap = {
            'idle': 'gray',
            'connecting': 'blue',
            'listening': 'red',
            'processing': 'orange',
            'speaking': 'green',
            'error': 'red'
        };
        
        return colorMap[this.currentState] || 'gray';
    }
    
    /**
     * 更新按钮状态
     */
    updateButtonStates() {
        const startBtn = document.getElementById('voice-call-btn');
        if (startBtn) {
            startBtn.disabled = this.isActive;
            startBtn.textContent = this.isActive ? '停止实时对话' : '开始实时对话';
        }
    }
    
    /**
     * 更新可视化
     */
    updateVisualization() {
        // 这里可以添加音频可视化更新逻辑
        this.emit('visualization_update', { state: this.currentState });
    }
    
    /**
     * 保存到记忆
     */
    async saveToMemory(content) {
        try {
            await this.adapterClient.saveMemory(
                this.conversationId,
                content,
                { type: 'realtime_voice', timestamp: new Date().toISOString() }
            );
        } catch (error) {
            console.error('保存记忆失败:', error);
        }
    }
    
    /**
     * 生成会话ID
     */
    generateConversationId() {
        return `realtime_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * 设置配置
     */
    setConfig(config) {
        this.config = { ...this.config, ...config };
        
        if (config.backendUrl) {
            this.adapterClient.setBackendUrl(config.backendUrl);
        }
        
        if (config.apiKey) {
            this.adapterClient.setApiKey(config.apiKey);
        }
    }
    
    /**
     * 获取状态
     */
    getState() {
        return {
            isActive: this.isActive,
            currentState: this.currentState,
            conversationId: this.conversationId,
            personalityId: this.personalityId
        };
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
    
    /**
     * 清理资源
     */
    cleanup() {
        if (this.isActive) {
            this.stop();
        }
        
        this.audioProcessor.cleanup();
        this.apiClient.disconnect();
        this.eventHandlers = {};
    }
}

// 全局实例
window.realtimeVoiceManager = new RealtimeVoiceManager();

// 导出类
window.RealtimeVoiceManager = RealtimeVoiceManager;
