/**
 * 状态同步管理器
 * 提供状态注册、监听、更新和UI同步功能
 */
class StateSyncManager {
    constructor() {
        this.states = new Map();
        this.listeners = new Map();
        this.updateQueue = [];
        this.isProcessing = false;
        this.syncInterval = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        window.controlledLog?.log('🔄 状态同步管理器已初始化');
        this.isInitialized = true;
        
        // 启动同步处理
        this.startSyncProcessing();
        
        // 集成智能状态预测器
        this.initSmartStatePredictor();
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // 监听窗口焦点变化
        window.addEventListener('focus', () => {
            this.handleWindowFocus();
        });
        
        window.addEventListener('blur', () => {
            this.handleWindowBlur();
        });
    }
    
    /**
     * 注册状态
     */
    registerState(stateName, initialState = {}) {
        if (this.states.has(stateName)) {
            console.warn(`🔄 状态 ${stateName} 已存在，将被覆盖`);
        }
        
        this.states.set(stateName, {
            ...initialState,
            _metadata: {
                createdAt: Date.now(),
                lastUpdated: Date.now(),
                version: 1
            }
        });
        
        window.controlledLog?.log(`🔄 状态 ${stateName} 已注册`);
        return this.getState(stateName);
    }
    
    /**
     * 获取状态
     */
    getState(stateName) {
        return this.states.get(stateName);
    }
    
    /**
     * 更新状态
     */
    updateState(stateName, updates, options = {}) {
        let currentState = this.states.get(stateName);
        if (!currentState) {
            // 如果状态不存在，尝试自动注册默认状态
            window.controlledLog?.log(`🔄 状态 ${stateName} 不存在，尝试自动注册`);
            this.registerState(stateName, {
                status: 'idle',
                isConnected: false,
                isConnecting: false,
                error: null
            });
            // 重新获取状态
            currentState = this.states.get(stateName);
        }
        
        // 确保 _metadata 存在
        const metadata = currentState._metadata || {
            created: Date.now(),
            lastUpdated: Date.now(),
            version: 0
        };
        
        const newState = {
            ...currentState,
            ...updates,
            _metadata: {
                ...metadata,
                lastUpdated: Date.now(),
                version: metadata.version + 1
            }
        };
        
        this.states.set(stateName, newState);
        
        // 添加到更新队列
        this.addToUpdateQueue(stateName, newState, options);
        
        window.controlledLog?.log(`🔄 状态 ${stateName} 已更新`);
        return true;
    }
    
    /**
     * 监听状态变化
     */
    addStateListener(stateName, callback, options = {}) {
        if (!this.listeners.has(stateName)) {
            this.listeners.set(stateName, []);
        }
        
        const listener = {
            callback,
            options,
            id: this.generateListenerId()
        };
        
        this.listeners.get(stateName).push(listener);
        
        window.controlledLog?.log(`🔄 状态监听器已添加: ${stateName}`);
        return listener.id;
    }
    
    /**
     * 移除状态监听器
     */
    removeStateListener(stateName, listenerId) {
        const listeners = this.listeners.get(stateName);
        if (!listeners) return false;
        
        const index = listeners.findIndex(l => l.id === listenerId);
        if (index === -1) return false;
        
        listeners.splice(index, 1);
        window.controlledLog?.log(`🔄 状态监听器已移除: ${stateName}`);
        return true;
    }
    
    /**
     * 添加状态更新到队列
     */
    addToUpdateQueue(stateName, newState, options = {}) {
        this.updateQueue.push({
            stateName,
            newState,
            options,
            timestamp: Date.now()
        });
        
        // 如果队列过长，清理旧更新
        if (this.updateQueue.length > 100) {
            this.updateQueue = this.updateQueue.slice(-50);
        }
    }
    
    /**
     * 启动同步处理
     */
    startSyncProcessing() {
        if (this.syncInterval) return;
        
        this.syncInterval = setInterval(() => {
            this.processUpdateQueue();
        }, 100); // 每100ms处理一次更新队列
    }
    
    /**
     * 停止同步处理
     */
    stopSyncProcessing() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }
    
    /**
     * 处理更新队列
     */
    processUpdateQueue() {
        if (this.isProcessing || this.updateQueue.length === 0) return;
        
        this.isProcessing = true;
        
        try {
            const updates = [...this.updateQueue];
            this.updateQueue = [];
            
            // 按状态名分组处理
            const groupedUpdates = this.groupUpdatesByState(updates);
            
            for (const [stateName, stateUpdates] of groupedUpdates) {
                this.processStateUpdates(stateName, stateUpdates);
            }
        } finally {
            this.isProcessing = false;
        }
    }
    
    /**
     * 按状态名分组更新
     */
    groupUpdatesByState(updates) {
        const grouped = new Map();
        
        updates.forEach(update => {
            if (!grouped.has(update.stateName)) {
                grouped.set(update.stateName, []);
            }
            grouped.get(update.stateName).push(update);
        });
        
        return grouped;
    }
    
    /**
     * 处理状态更新
     */
    processStateUpdates(stateName, updates) {
        const listeners = this.listeners.get(stateName);
        if (!listeners || listeners.length === 0) return;
        
        // 获取最新状态
        const latestUpdate = updates[updates.length - 1];
        const newState = latestUpdate.newState;
        
        // 通知所有监听器
        listeners.forEach(listener => {
            try {
                listener.callback(newState, latestUpdate.options);
            } catch (error) {
                console.error(`🔄 状态监听器错误 (${stateName}):`, error);
            }
        });
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        const isVisible = !document.hidden;
        
        if (isVisible) {
            window.controlledLog?.log('🔄 页面变为可见，同步所有状态');
            this.syncAllStates();
        } else {
            window.controlledLog?.log('🔄 页面变为隐藏，暂停非关键状态更新');
            this.pauseNonCriticalUpdates();
        }
    }
    
    /**
     * 处理窗口焦点变化
     */
    handleWindowFocus() {
        window.controlledLog?.log('🔄 窗口获得焦点，同步状态');
        this.syncAllStates();
    }
    
    handleWindowBlur() {
        window.controlledLog?.log('🔄 窗口失去焦点，暂停状态更新');
        this.pauseNonCriticalUpdates();
    }
    
    /**
     * 同步所有状态
     */
    syncAllStates() {
        for (const [stateName, state] of this.states) {
            this.triggerStateSync(stateName, state);
        }
    }
    
    /**
     * 触发状态同步
     */
    triggerStateSync(stateName, state) {
        const listeners = this.listeners.get(stateName);
        if (!listeners) return;
        
        listeners.forEach(listener => {
            if (listener.options.syncOnFocus !== false) {
                try {
                    listener.callback(state, { sync: true });
                } catch (error) {
                    console.error(`🔄 状态同步错误 (${stateName}):`, error);
                }
            }
        });
    }
    
    /**
     * 暂停非关键状态更新
     */
    pauseNonCriticalUpdates() {
        // 标记非关键状态为暂停
        for (const [stateName, state] of this.states) {
            if (state._metadata && !state._metadata.critical) {
                this.updateState(stateName, { _paused: true });
            }
        }
    }
    
    /**
     * 恢复状态更新
     */
    resumeUpdates() {
        for (const [stateName, state] of this.states) {
            if (state._paused) {
                this.updateState(stateName, { _paused: false });
            }
        }
    }
    
    /**
     * 创建状态快照
     */
    createSnapshot() {
        const snapshot = {};
        
        for (const [stateName, state] of this.states) {
            snapshot[stateName] = {
                ...state,
                _snapshot: true,
                _timestamp: Date.now()
            };
        }
        
        return snapshot;
    }
    
    /**
     * 恢复状态快照
     */
    restoreSnapshot(snapshot) {
        for (const [stateName, stateData] of Object.entries(snapshot)) {
            if (stateData._snapshot) {
                this.states.set(stateName, {
                    ...stateData,
                    _metadata: {
                        ...stateData._metadata,
                        lastUpdated: Date.now(),
                        restored: true
                    }
                });
            }
        }
        
        window.controlledLog?.log('🔄 状态快照已恢复');
    }
    
    /**
     * 获取状态统计
     */
    getStats() {
        const stats = {
            totalStates: this.states.size,
            totalListeners: 0,
            pendingUpdates: this.updateQueue.length,
            isProcessing: this.isProcessing
        };
        
        for (const listeners of this.listeners.values()) {
            stats.totalListeners += listeners.length;
        }
        
        return stats;
    }
    
    /**
     * 清理状态
     */
    cleanup() {
        this.states.clear();
        this.listeners.clear();
        this.updateQueue = [];
        this.stopSyncProcessing();
        window.controlledLog?.log('🔄 状态同步管理器已清理');
    }
    
    /**
     * 初始化智能状态预测器
     */
    initSmartStatePredictor() {
        if (window.smartStatePredictor) {
            window.controlledLog?.log('🔮 智能状态预测器已连接');
            
            // 监听状态变化，记录用户行为
            this.addGlobalStateListener();
        } else {
            console.warn('🔮 智能状态预测器未找到');
        }
    }
    
    /**
     * 添加全局状态监听器
     */
    addGlobalStateListener() {
        // 监听所有状态变化
        const originalUpdateState = this.updateState.bind(this);
        this.updateState = (stateName, updates, options = {}) => {
            // 调用原始更新方法
            const result = originalUpdateState(stateName, updates, options);
            
            // 记录用户行为到智能状态预测器
            if (window.smartStatePredictor && result) {
                const currentState = this.getState(stateName);
                if (currentState) {
                    window.smartStatePredictor.recordUserAction('state_change', {
                        stateName: stateName,
                        newState: currentState,
                        updates: updates,
                        timestamp: Date.now()
                    });
                }
            }
            
            return result;
        };
    }
    
    /**
     * 生成监听器ID
     */
    generateListenerId() {
        return `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * 调试信息
     */
    debug() {
        window.controlledLog?.log('🔄 状态同步管理器调试信息:', {
            states: Array.from(this.states.keys()),
            listeners: Array.from(this.listeners.entries()).map(([name, listeners]) => ({
                state: name,
                count: listeners.length
            })),
            queue: this.updateQueue.length,
            stats: this.getStats()
        });
    }
}

// 初始化状态同步管理器
let stateSyncManager;

function initStateSyncManager() {
    if (!stateSyncManager) {
        stateSyncManager = new StateSyncManager();
        window.stateSyncManager = stateSyncManager;
        window.controlledLog?.log('🔄 状态同步管理器已启动');
    }
}

// 页面加载完成后初始化（仅在聊天页面）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.chatPageConfig && window.chatPageConfig.isChatPage) {
            initStateSyncManager();
        }
    });
} else {
    if (window.chatPageConfig && window.chatPageConfig.isChatPage) {
        initStateSyncManager();
    }
}