/**
 * JavaScript状态管理器
 * 
 * 提供与Python状态管理器对应的JavaScript实现，包括状态定义、状态转换、状态锁定等。
 * 
 * 作者: AI Assistant
 * 创建时间: 2024-10-24
 * 版本: 1.0.0
 */

class StateManager {
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
    }
    
    /**
     * 设置状态
     * @param {string} newState - 新状态
     * @returns {boolean} 是否设置成功
     */
    setState(newState) {
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
            timestamp: Date.now()
        });
        
        // 更新状态
        this.currentState = newState;
        
        // 触发状态变化回调
        this.stateChangeCallbacks.forEach(callback => {
            try {
                callback(previousState, newState);
            } catch (error) {
                console.error('状态变化回调执行失败:', error);
            }
        });
        
        console.log(`状态转换成功: ${previousState} -> ${newState}`);
        return true;
    }
    
    /**
     * 获取当前状态
     * @returns {string} 当前状态
     */
    getState() {
        return this.currentState;
    }
    
    /**
     * 检查状态转换是否合法
     * @param {string} newState - 目标状态
     * @returns {boolean} 是否可以转换
     */
    canTransition(newState) {
        return this.stateTransitions[this.currentState]?.includes(newState) || false;
    }
    
    /**
     * 锁定状态
     * @param {number} duration - 锁定持续时间（毫秒），undefined表示永久锁定
     */
    lockState(duration) {
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
     * @returns {boolean} 是否被锁定
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
     * @returns {boolean} 是否回滚成功
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
     * 获取状态历史
     * @returns {Array} 状态历史列表
     */
    getStateHistory() {
        return [...this.stateHistory];
    }
    
    /**
     * 清空状态历史
     */
    clearStateHistory() {
        this.stateHistory = [];
        console.log('状态历史已清空');
    }
    
    /**
     * 注册状态变化回调
     * @param {Function} callback - 回调函数，接收 (fromState, toState) 参数
     */
    registerStateChangeCallback(callback) {
        this.stateChangeCallbacks.push(callback);
        console.log('状态变化回调已注册');
    }
    
    /**
     * 注销状态变化回调
     * @param {Function} callback - 要注销的回调函数
     */
    unregisterStateChangeCallback(callback) {
        const index = this.stateChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.stateChangeCallbacks.splice(index, 1);
            console.log('状态变化回调已注销');
        }
    }
    
    /**
     * 获取可用的状态转换
     * @returns {Array} 可转换的状态列表
     */
    getAvailableTransitions() {
        return this.stateTransitions[this.currentState] || [];
    }
    
    /**
     * 强制设置状态（忽略转换规则和锁定）
     * @param {string} newState - 新状态
     * @returns {boolean} 是否设置成功
     */
    forceSetState(newState) {
        const previousState = this.currentState;
        this.currentState = newState;
        
        // 记录强制状态变化
        this.stateHistory.push({
            from: previousState,
            to: newState,
            timestamp: Date.now(),
            forced: true
        });
        
        console.warn(`强制状态转换: ${previousState} -> ${newState}`);
        return true;
    }
    
    /**
     * 重置到空闲状态
     * @returns {boolean} 是否重置成功
     */
    resetToIdle() {
        if (this.currentState === 'idle') {
            return true;
        }
        
        // 清空历史并强制设置为IDLE
        this.stateHistory = [];
        this.stateLocked = false;
        this.currentState = 'idle';
        
        console.log('状态已重置到空闲状态');
        return true;
    }
    
    /**
     * 获取状态信息
     * @returns {Object} 状态信息字典
     */
    getStateInfo() {
        return {
            currentState: this.currentState,
            isLocked: this.isStateLocked(),
            lockTime: this.stateLockTime,
            availableTransitions: this.getAvailableTransitions(),
            historyCount: this.stateHistory.length,
            maxLockDuration: this.maxLockDuration
        };
    }
    
    /**
     * 检查状态是否为特定值
     * @param {string} state - 状态值
     * @returns {boolean} 是否匹配
     */
    isState(state) {
        return this.currentState === state;
    }
    
    /**
     * 检查状态是否在特定列表中
     * @param {Array} states - 状态列表
     * @returns {boolean} 是否在列表中
     */
    isStateIn(states) {
        return states.includes(this.currentState);
    }
    
    /**
     * 获取状态持续时间
     * @returns {number} 持续时间（毫秒）
     */
    getStateDuration() {
        if (this.stateHistory.length === 0) {
            return 0;
        }
        
        const lastTransition = this.stateHistory[this.stateHistory.length - 1];
        return Date.now() - lastTransition.timestamp;
    }
    
    /**
     * 获取状态统计
     * @returns {Object} 状态统计
     */
    getStateStats() {
        const stats = {};
        this.stateHistory.forEach(transition => {
            stats[transition.to] = (stats[transition.to] || 0) + 1;
        });
        return stats;
    }
}

// 便捷函数
/**
 * 创建状态管理器
 * @returns {StateManager} 状态管理器实例
 */
function createStateManager() {
    return new StateManager();
}

/**
 * 获取状态名称
 * @param {string} state - 状态值
 * @returns {string} 状态名称
 */
function getStateName(state) {
    return state;
}

/**
 * 检查状态名称是否有效
 * @param {string} stateName - 状态名称
 * @returns {boolean} 是否有效
 */
function isValidState(stateName) {
    const validStates = [
        'idle', 'text_sse', 'text_tts', 'voice_stt', 
        'voice_sse', 'voice_tts', 'voice_call', 'error'
    ];
    return validStates.includes(stateName);
}

// 全局状态管理器实例
window.stateManager = new StateManager();

// 便捷函数
/**
 * 获取配置值的便捷函数
 * @param {string} key - 配置键
 * @param {*} defaultValue - 默认值
 * @returns {*} 配置值
 */
window.getState = function() {
    return window.stateManager.getState();
};

/**
 * 设置状态的便捷函数
 * @param {string} state - 状态值
 * @returns {boolean} 是否设置成功
 */
window.setState = function(state) {
    return window.stateManager.setState(state);
};

/**
 * 检查状态的便捷函数
 * @param {string} state - 状态值
 * @returns {boolean} 是否匹配
 */
window.isState = function(state) {
    return window.stateManager.isState(state);
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript状态管理器已初始化');
    console.log('当前状态:', window.stateManager.getState());
});
