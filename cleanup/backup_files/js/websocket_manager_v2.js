/**
 * WebSocket管理器 V2
 * 
 * 优化后的WebSocket连接管理，集成新的状态管理器。
 * 
 * 作者: AI Assistant
 * 创建时间: 2024-10-24
 * 版本: 2.0.0
 */

class WebSocketManagerV2 {
    /**
     * 构造函数
     */
    constructor() {
        this.websocket = null;
        this.connectionState = 'disconnected';
        this.url = window.getConfig('websocket.url', 'ws://localhost:8000/ws');
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = window.getConfig('websocket.reconnectAttempts', 5);
        this.reconnectInterval = window.getConfig('websocket.reconnectInterval', 5000);
        this.heartbeatInterval = window.getConfig('websocket.heartbeatInterval', 30000);
        
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        this.messageHandlers = [];
        this.connectionHandlers = [];
        this.errorHandlers = [];
        
        this.messageQueue = [];
        this.maxQueueSize = 100;
        this.lastHeartbeat = null;
        this.heartbeatTimeout = 10000; // 10秒心跳超时
        
        // 绑定方法
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
        this.handleMessage = this.handleMessage.bind(this);
        this.handleError = this.handleError.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.startHeartbeat = this.startHeartbeat.bind(this);
        this.stopHeartbeat = this.stopHeartbeat.bind(this);
        this.scheduleReconnect = this.scheduleReconnect.bind(this);
    }
    
    /**
     * 连接WebSocket
     */
    async connect() {
        if (this.connectionState === 'connected' || this.connectionState === 'connecting') {
            console.log('WebSocket已连接或正在连接中');
            return true;
        }
        
        try {
            this.connectionState = 'connecting';
            console.log(`正在连接WebSocket: ${this.url}`);
            
            this.websocket = new WebSocket(this.url);
            
            this.websocket.onopen = () => {
                this.connectionState = 'connected';
                this.reconnectAttempts = 0;
                console.log('WebSocket连接成功');
                
                // 启动心跳
                this.startHeartbeat();
                
                // 发送队列中的消息
                this.sendQueuedMessages();
                
                // 通知连接处理器
                this.notifyConnectionHandlers(true);
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event);
            };
            
            this.websocket.onerror = (error) => {
                this.handleError(error);
            };
            
            this.websocket.onclose = (event) => {
                this.handleClose(event);
            };
            
            return true;
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.connectionState = 'error';
            this.notifyErrorHandlers(`连接失败: ${error.message}`);
            return false;
        }
    }
    
    /**
     * 断开WebSocket连接
     */
    disconnect() {
        if (this.connectionState === 'disconnected') {
            return;
        }
        
        console.log('正在断开WebSocket连接');
        
        // 停止心跳
        this.stopHeartbeat();
        
        // 停止重连
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        // 关闭连接
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.connectionState = 'disconnected';
        this.notifyConnectionHandlers(false);
        
        console.log('WebSocket连接已断开');
    }
    
    /**
     * 发送消息
     */
    async sendMessage(message) {
        if (this.connectionState !== 'connected') {
            console.warn('WebSocket未连接，消息已加入队列');
            this.queueMessage(message);
            return false;
        }
        
        try {
            const messageStr = JSON.stringify(message);
            this.websocket.send(messageStr);
            console.log(`消息已发送: ${message.type || 'unknown'}`);
            return true;
        } catch (error) {
            console.error('发送消息失败:', error);
            this.notifyErrorHandlers(`发送消息失败: ${error.message}`);
            return false;
        }
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            // 处理心跳响应
            if (data.type === 'heartbeat') {
                this.lastHeartbeat = Date.now();
                return;
            }
            
            // 通知消息处理器
            this.messageHandlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error('消息处理器执行失败:', error);
                }
            });
            
        } catch (error) {
            console.error('解析消息失败:', error);
        }
    }
    
    /**
     * 处理错误
     */
    handleError(error) {
        console.error('WebSocket错误:', error);
        this.connectionState = 'error';
        this.notifyErrorHandlers(`WebSocket错误: ${error.message || '未知错误'}`);
    }
    
    /**
     * 处理连接关闭
     */
    handleClose(event) {
        console.warn('WebSocket连接已关闭:', event.code, event.reason);
        this.connectionState = 'disconnected';
        this.websocket = null;
        
        // 停止心跳
        this.stopHeartbeat();
        
        // 通知连接处理器
        this.notifyConnectionHandlers(false);
        
        // 启动重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            console.error('已达到最大重连次数，停止重连');
            this.notifyErrorHandlers('WebSocket连接失败，已达到最大重连次数');
        }
    }
    
    /**
     * 启动心跳检测
     */
    startHeartbeat() {
        if (this.heartbeatTimer) {
            return;
        }
        
        this.heartbeatTimer = setInterval(() => {
            if (this.connectionState === 'connected') {
                // 发送心跳
                this.sendMessage({
                    type: 'heartbeat',
                    timestamp: Date.now()
                });
                
                // 检查心跳超时
                if (this.lastHeartbeat && Date.now() - this.lastHeartbeat > this.heartbeatTimeout) {
                    console.warn('心跳超时，触发重连');
                    this.handleClose({ code: 1000, reason: 'heartbeat timeout' });
                }
            }
        }, this.heartbeatInterval);
        
        console.log('心跳检测已启动');
    }
    
    /**
     * 停止心跳检测
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
            console.log('心跳检测已停止');
        }
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = Math.min(
            this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
            30000 // 最大30秒
        );
        
        console.log(`将在 ${delay}ms 后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        this.reconnectTimer = setTimeout(() => {
            if (this.connectionState === 'disconnected') {
                console.log('开始自动重连...');
                this.connect();
            }
        }, delay);
    }
    
    /**
     * 将消息加入队列
     */
    queueMessage(message) {
        if (this.messageQueue.length >= this.maxQueueSize) {
            console.warn('消息队列已满，丢弃最旧的消息');
            this.messageQueue.shift();
        }
        
        this.messageQueue.push({
            message: message,
            timestamp: Date.now()
        });
    }
    
    /**
     * 发送队列中的消息
     */
    async sendQueuedMessages() {
        if (this.messageQueue.length === 0) {
            return;
        }
        
        console.log(`发送队列中的 ${this.messageQueue.length} 条消息`);
        
        const messages = [...this.messageQueue];
        this.messageQueue = [];
        
        for (const item of messages) {
            try {
                await this.sendMessage(item.message);
            } catch (error) {
                console.error('发送队列消息失败:', error);
                // 重新加入队列
                this.messageQueue.push(item);
                break;
            }
        }
    }
    
    /**
     * 注册消息处理器
     */
    registerMessageHandler(handler) {
        this.messageHandlers.push(handler);
        console.log('消息处理器已注册');
    }
    
    /**
     * 注销消息处理器
     */
    unregisterMessageHandler(handler) {
        const index = this.messageHandlers.indexOf(handler);
        if (index > -1) {
            this.messageHandlers.splice(index, 1);
            console.log('消息处理器已注销');
        }
    }
    
    /**
     * 注册连接状态处理器
     */
    registerConnectionHandler(handler) {
        this.connectionHandlers.push(handler);
        console.log('连接状态处理器已注册');
    }
    
    /**
     * 注销连接状态处理器
     */
    unregisterConnectionHandler(handler) {
        const index = this.connectionHandlers.indexOf(handler);
        if (index > -1) {
            this.connectionHandlers.splice(index, 1);
            console.log('连接状态处理器已注销');
        }
    }
    
    /**
     * 注册错误处理器
     */
    registerErrorHandler(handler) {
        this.errorHandlers.push(handler);
        console.log('错误处理器已注册');
    }
    
    /**
     * 注销错误处理器
     */
    unregisterErrorHandler(handler) {
        const index = this.errorHandlers.indexOf(handler);
        if (index > -1) {
            this.errorHandlers.splice(index, 1);
            console.log('错误处理器已注销');
        }
    }
    
    /**
     * 通知连接状态处理器
     */
    notifyConnectionHandlers(connected) {
        this.connectionHandlers.forEach(handler => {
            try {
                handler(connected);
            } catch (error) {
                console.error('连接状态处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 通知错误处理器
     */
    notifyErrorHandlers(error) {
        this.errorHandlers.forEach(handler => {
            try {
                handler(error);
            } catch (error) {
                console.error('错误处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 检查是否已连接
     */
    isConnected() {
        return this.connectionState === 'connected';
    }
    
    /**
     * 获取连接状态
     */
    getConnectionState() {
        return this.connectionState;
    }
    
    /**
     * 获取连接信息
     */
    getConnectionInfo() {
        return {
            state: this.connectionState,
            url: this.url,
            attempts: this.reconnectAttempts,
            maxAttempts: this.maxReconnectAttempts,
            queueSize: this.messageQueue.length,
            lastHeartbeat: this.lastHeartbeat,
            handlers: {
                message: this.messageHandlers.length,
                connection: this.connectionHandlers.length,
                error: this.errorHandlers.length
            }
        };
    }
    
    /**
     * 强制重连
     */
    async forceReconnect() {
        console.log('强制重连WebSocket');
        
        // 断开当前连接
        this.disconnect();
        
        // 重置重连计数
        this.reconnectAttempts = 0;
        
        // 重新连接
        return await this.connect();
    }
}

// 全局WebSocket管理器实例
window.websocketManagerV2 = new WebSocketManagerV2();

// 便捷函数
window.connectWebSocket = function() {
    return window.websocketManagerV2.connect();
};

window.disconnectWebSocket = function() {
    return window.websocketManagerV2.disconnect();
};

window.sendWebSocketMessage = function(message) {
    return window.websocketManagerV2.sendMessage(message);
};

window.isWebSocketConnected = function() {
    return window.websocketManagerV2.isConnected();
};

// 页面加载完成后自动连接
document.addEventListener('DOMContentLoaded', function() {
    console.log('WebSocket管理器V2已初始化');
    
    // 自动连接
    window.websocketManagerV2.connect();
});
