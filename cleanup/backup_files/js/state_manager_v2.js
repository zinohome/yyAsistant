/**
 * JavaScript状态管理器 V2
 * 
 * 集成超时和错误处理的状态管理器。
 * 
 * 作者: AI Assistant
 * 创建时间: 2024-10-24
 * 版本: 2.0.0
 */

class StateManagerV2 {
    /**
     * 构造函数
     */
    constructor() {
        this.currentState = 'idle';
        this.stateHistory = [];
        this.stateLocked = false;
        this.stateTransitions = {
            'idle': ['text_sse', 'voice_stt', 'voice_call'],
            'text_sse': ['text_tts', 'idle', 'error'],
            'text_tts': ['idle', 'error'],
            'voice_stt': ['voice_sse', 'idle', 'error'],
            'voice_sse': ['voice_tts', 'idle', 'error'],
            'voice_tts': ['idle', 'error'],
            'voice_call': ['idle', 'error'],
            'error': ['idle']
        };
        this.stateChangeCallbacks = [];
        this.stateLockTime = null;
        this.maxLockDuration = 300000; // 5分钟最大锁定时间（毫秒）
        
        // 超时管理
        this.activeTimeouts = {};
        this.timeoutConfig = {
            sse: { base: 30, perChar: 0.1, max: 300 },
            tts: { base: 60, perChar: 0.2, max: 600 },
            stt: { base: 30, perChar: 0.05, max: 180 }
        };
        this.warningThreshold = 0.8;
        
        // 错误处理
        this.errorHandlers = [];
        this.autoRecovery = true;
        
        // 状态统计
        this.stateStats = {};
        this.initializeStats();
    }
    
    /**
     * 初始化统计
     */
    initializeStats() {
        const states = Object.keys(this.stateTransitions);
        states.forEach(state => {
            this.stateStats[state] = 0;
        });
    }
    
    /**
     * 设置状态
     */
    setState(newState, data = null) {
        if (this.stateLocked) {
            console.warn(`状态已锁定，无法从 ${this.currentState} 转换到 ${newState}`);
            return false;
        }
        
        if (!this.canTransition(newState)) {
            console.warn(`无效的状态转换：从 ${this.currentState} 到 ${newState}`);
            return false;
        }
        
        // 记录状态历史
        const previousState = this.currentState;
        this.stateHistory.push({
            from: previousState,
            to: newState,
            timestamp: Date.now(),
            data: data
        });
        
        // 更新状态
        this.currentState = newState;
        this.stateStats[newState]++;
        
        // 触发状态变化回调
        this.stateChangeCallbacks.forEach(callback => {
            try {
                callback(previousState, newState, data);
            } catch (error) {
                console.error('状态变化回调执行失败:', error);
            }
        });
        
        console.log(`状态转换成功: ${previousState} -> ${newState}`);
        return true;
    }
    
    /**
     * 获取当前状态
     */
    getState() {
        return this.currentState;
    }
    
    /**
     * 检查状态转换是否合法
     */
    canTransition(newState) {
        return this.stateTransitions[this.currentState]?.includes(newState) || false;
    }
    
    /**
     * 锁定状态
     */
    lockState(duration = null) {
        this.stateLocked = true;
        this.stateLockTime = Date.now();
        if (duration) {
            this.maxLockDuration = duration;
        }
        console.log(`状态已锁定，持续时间: ${duration ? duration + 'ms' : '永久'}`);
    }
    
    /**
     * 解锁状态
     */
    unlockState() {
        this.stateLocked = false;
        this.stateLockTime = null;
        console.log('状态已解锁');
    }
    
    /**
     * 检查状态是否被锁定
     */
    isStateLocked() {
        if (!this.stateLocked) {
            return false;
        }
        
        // 检查锁定是否超时
        if (this.stateLockTime && Date.now() - this.stateLockTime > this.maxLockDuration) {
            console.warn('状态锁定超时，自动解锁');
            this.unlockState();
            return false;
        }
        
        return true;
    }
    
    /**
     * 回滚状态
     */
    rollbackState() {
        if (this.stateHistory.length === 0) {
            console.warn('没有状态历史可以回滚');
            return false;
        }
        
        const previousStateInfo = this.stateHistory.pop();
        const previousState = previousStateInfo.from;
        
        // 直接设置状态，不检查转换规则
        this.currentState = previousState;
        
        console.log(`状态已回滚到: ${previousState}`);
        return true;
    }
    
    /**
     * 启动超时
     */
    startTimeout(timeoutId, contentLength, timeoutType) {
        const config = this.timeoutConfig[timeoutType];
        if (!config) {
            console.warn(`未知的超时类型: ${timeoutType}`);
            return false;
        }
        
        // 计算超时时间
        const baseTimeout = config.base;
        const perCharTimeout = config.perChar * contentLength;
        const maxTimeout = config.max;
        
        const totalTimeout = Math.min(baseTimeout + perCharTimeout, maxTimeout);
        const warningTime = totalTimeout * this.warningThreshold;
        
        const timeoutInfo = {
            id: timeoutId,
            type: timeoutType,
            duration: totalTimeout,
            warningTime: warningTime,
            startTime: Date.now(),
            contentLength: contentLength,
            warned: false,
            active: true
        };
        
        this.activeTimeouts[timeoutId] = timeoutInfo;
        
        // 启动超时检查
        this.scheduleTimeoutCheck(timeoutId, warningTime, totalTimeout);
        
        console.log(`超时已启动: ${timeoutId}, 类型: ${timeoutType}, 时长: ${totalTimeout}s`);
        return true;
    }
    
    /**
     * 安排超时检查
     */
    scheduleTimeoutCheck(timeoutId, warningTime, timeoutDuration) {
        // 警告检查
        setTimeout(() => {
            this.checkTimeoutWarning(timeoutId);
        }, warningTime);
        
        // 超时检查
        setTimeout(() => {
            this.checkTimeout(timeoutId);
        }, timeoutDuration);
    }
    
    /**
     * 检查超时警告
     */
    checkTimeoutWarning(timeoutId) {
        if (!this.activeTimeouts[timeoutId] || !this.activeTimeouts[timeoutId].active) {
            return;
        }
        
        this.activeTimeouts[timeoutId].warned = true;
        console.warn(`超时警告: ${timeoutId} 即将超时`);
        
        // 触发警告事件
        this.triggerEvent('timeout_warning', {
            timeoutId: timeoutId,
            timeoutInfo: this.activeTimeouts[timeoutId]
        });
    }
    
    /**
     * 检查超时
     */
    checkTimeout(timeoutId) {
        if (!this.activeTimeouts[timeoutId] || !this.activeTimeouts[timeoutId].active) {
            return;
        }
        
        this.activeTimeouts[timeoutId].active = false;
        this.activeTimeouts[timeoutId].timedOut = true;
        
        console.error(`超时发生: ${timeoutId}`);
        
        // 触发超时事件
        this.triggerEvent('timeout', {
            timeoutId: timeoutId,
            timeoutInfo: this.activeTimeouts[timeoutId]
        });
        
        // 处理超时
        this.handleTimeout(timeoutId, this.activeTimeouts[timeoutId]);
    }
    
    /**
     * 处理超时
     */
    handleTimeout(timeoutId, timeoutInfo) {
        const timeoutType = timeoutInfo.type;
        const contentLength = timeoutInfo.contentLength;
        
        // 检查是否为长文本TTS
        if (timeoutType === 'tts' && contentLength > 1000) {
            // 长文本TTS显示警告但继续处理
            this.triggerEvent('long_text_tts_warning', {
                timeoutId: timeoutId,
                message: '长文本TTS处理中，请耐心等待...',
                timeoutInfo: timeoutInfo
            });
        } else {
            // 其他超时停止处理
            this.triggerEvent('timeout_stop', {
                timeoutId: timeoutId,
                message: '处理超时，已停止',
                timeoutInfo: timeoutInfo
            });
            
            // 转换到错误状态
            this.setState('error', {
                type: 'timeout',
                timeoutId: timeoutId,
                timeoutInfo: timeoutInfo
            });
        }
    }
    
    /**
     * 取消超时
     */
    cancelTimeout(timeoutId) {
        if (this.activeTimeouts[timeoutId]) {
            this.activeTimeouts[timeoutId].active = false;
            this.activeTimeouts[timeoutId].cancelled = true;
            console.log(`超时已取消: ${timeoutId}`);
            return true;
        }
        return false;
    }
    
    /**
     * 延长超时
     */
    extendTimeout(timeoutId, additionalTime) {
        if (!this.activeTimeouts[timeoutId] || !this.activeTimeouts[timeoutId].active) {
            return false;
        }
        
        this.activeTimeouts[timeoutId].duration += additionalTime;
        this.activeTimeouts[timeoutId].warningTime = this.activeTimeouts[timeoutId].duration * this.warningThreshold;
        
        console.log(`超时已延长: ${timeoutId}, 额外时间: ${additionalTime}s`);
        return true;
    }
    
    /**
     * 处理错误
     */
    handleError(errorType, errorData, severity = 'medium') {
        console.error(`错误发生: ${errorType}`, errorData);
        
        // 记录错误
        const errorRecord = {
            type: errorType,
            data: errorData,
            severity: severity,
            timestamp: Date.now(),
            state: this.currentState
        };
        
        // 通知错误处理器
        this.errorHandlers.forEach(handler => {
            try {
                handler(errorRecord);
            } catch (error) {
                console.error('错误处理器执行失败:', error);
            }
        });
        
        // 转换到错误状态
        this.setState('error', errorRecord);
        
        // 自动恢复
        if (this.autoRecovery) {
            this.attemptRecovery(errorType, errorData);
        }
    }
    
    /**
     * 尝试自动恢复
     */
    attemptRecovery(errorType, errorData) {
        console.log(`尝试自动恢复: ${errorType}`);
        
        // 根据错误类型选择恢复策略
        switch (errorType) {
            case 'websocket_connection':
                // WebSocket连接错误，尝试重连
                if (window.websocketManagerV2) {
                    window.websocketManagerV2.forceReconnect();
                }
                break;
            case 'timeout':
                // 超时错误，重置到空闲状态
                this.setState('idle');
                break;
            case 'state_transition':
                // 状态转换错误，回滚状态
                this.rollbackState();
                break;
            default:
                // 其他错误，重置到空闲状态
                this.setState('idle');
                break;
        }
    }
    
    /**
     * 触发事件
     */
    triggerEvent(eventType, data) {
        // 这里可以集成事件管理器
        console.log(`事件触发: ${eventType}`, data);
    }
    
    /**
     * 注册状态变化回调
     */
    registerStateChangeCallback(callback) {
        this.stateChangeCallbacks.push(callback);
        console.log('状态变化回调已注册');
    }
    
    /**
     * 注销状态变化回调
     */
    unregisterStateChangeCallback(callback) {
        const index = this.stateChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.stateChangeCallbacks.splice(index, 1);
            console.log('状态变化回调已注销');
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
     * 获取状态信息
     */
    getStateInfo() {
        return {
            currentState: this.currentState,
            isLocked: this.isStateLocked(),
            lockTime: this.stateLockTime,
            availableTransitions: this.getAvailableTransitions(),
            historyCount: this.stateHistory.length,
            maxLockDuration: this.maxLockDuration,
            activeTimeouts: Object.keys(this.activeTimeouts).length,
            stateStats: this.stateStats
        };
    }
    
    /**
     * 获取可用的状态转换
     */
    getAvailableTransitions() {
        return this.stateTransitions[this.currentState] || [];
    }
    
    /**
     * 获取活跃超时
     */
    getActiveTimeouts() {
        const active = {};
        for (const [timeoutId, timeoutInfo] of Object.entries(this.activeTimeouts)) {
            if (timeoutInfo.active) {
                const elapsed = Date.now() - timeoutInfo.startTime;
                const remaining = timeoutInfo.duration - elapsed;
                active[timeoutId] = {
                    id: timeoutId,
                    type: timeoutInfo.type,
                    duration: timeoutInfo.duration,
                    elapsed: elapsed,
                    remaining: Math.max(0, remaining),
                    active: timeoutInfo.active,
                    warned: timeoutInfo.warned,
                    contentLength: timeoutInfo.contentLength
                };
            }
        }
        return active;
    }
    
    /**
     * 重置到空闲状态
     */
    resetToIdle() {
        if (this.currentState === 'idle') {
            return true;
        }
        
        // 清空历史并强制设置为IDLE
        this.stateHistory = [];
        this.stateLocked = false;
        this.currentState = 'idle';
        
        // 取消所有活跃超时
        for (const timeoutId of Object.keys(this.activeTimeouts)) {
            this.cancelTimeout(timeoutId);
        }
        
        console.log('状态已重置到空闲状态');
        return true;
    }
    
    /**
     * 设置自动恢复
     */
    setAutoRecovery(enabled) {
        this.autoRecovery = enabled;
        console.log(`自动恢复已${enabled ? '启用' : '禁用'}`);
    }
    
    /**
     * 获取管理器信息
     */
    getManagerInfo() {
        return {
            currentState: this.currentState,
            isLocked: this.isStateLocked(),
            historyCount: this.stateHistory.length,
            activeTimeouts: Object.keys(this.activeTimeouts).length,
            stateStats: this.stateStats,
            autoRecovery: this.autoRecovery,
            handlers: {
                stateChange: this.stateChangeCallbacks.length,
                error: this.errorHandlers.length
            }
        };
    }
}

// 全局状态管理器实例
window.stateManagerV2 = new StateManagerV2();

// 便捷函数
window.getStateV2 = function() {
    return window.stateManagerV2.getState();
};

window.setStateV2 = function(state, data) {
    return window.stateManagerV2.setState(state, data);
};

window.isStateV2 = function(state) {
    return window.stateManagerV2.getState() === state;
};

window.startTimeoutV2 = function(timeoutId, contentLength, timeoutType) {
    return window.stateManagerV2.startTimeout(timeoutId, contentLength, timeoutType);
};

window.cancelTimeoutV2 = function(timeoutId) {
    return window.stateManagerV2.cancelTimeout(timeoutId);
};

window.handleErrorV2 = function(errorType, errorData, severity) {
    return window.stateManagerV2.handleError(errorType, errorData, severity);
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript状态管理器V2已初始化');
    console.log('当前状态:', window.stateManagerV2.getState());
});
