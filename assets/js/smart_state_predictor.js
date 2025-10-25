/**
 * 智能状态预测器
 * 基于用户行为分析预测下一个状态
 */
class SmartStatePredictor {
    constructor() {
        this.patterns = new Map();
        this.userBehavior = [];
        this.maxBehaviorHistory = 100;
        this.predictionCache = new Map();
        
        // 初始化常见模式
        this.initializeCommonPatterns();
    }
    
    /**
     * 初始化常见模式
     */
    initializeCommonPatterns() {
        // 文本聊天模式
        this.patterns.set('text_chat', {
            sequence: ['idle', 'text_processing', 'text_tts', 'idle'],
            probability: 0.8
        });
        
        // 录音聊天模式
        this.patterns.set('voice_recording', {
            sequence: ['idle', 'recording', 'voice_stt', 'voice_sse', 'voice_tts', 'idle'],
            probability: 0.7
        });
        
        // 语音通话模式
        this.patterns.set('voice_call', {
            sequence: ['idle', 'calling', 'idle'],
            probability: 0.6
        });
        
        window.controlledLog?.log('🔮 智能状态预测器已初始化，常见模式:', Array.from(this.patterns.keys()));
    }
    
    /**
     * 记录用户行为
     */
    recordUserAction(action, context = {}) {
        const behavior = {
            action: action,
            context: context,
            timestamp: Date.now(),
            outcome: null
        };
        
        this.userBehavior.push(behavior);
        
        // 保持行为历史在合理范围内
        if (this.userBehavior.length > this.maxBehaviorHistory) {
            this.userBehavior.shift();
        }
        
        // 更新模式
        this.updatePatterns();
        
        window.controlledLog?.log(`📝 记录用户行为: ${action}`, context);
    }
    
    /**
     * 更新模式
     */
    updatePatterns() {
        // 分析最近的行为序列
        const recentBehaviors = this.userBehavior.slice(-10);
        
        if (recentBehaviors.length < 3) {
            return; // 数据不足，无法分析
        }
        
        // 提取行为序列
        const sequence = recentBehaviors.map(b => b.action);
        
        // 查找匹配的模式
        const matchedPattern = this.findMatchingPattern(sequence);
        
        if (matchedPattern) {
            // 更新模式概率
            const pattern = this.patterns.get(matchedPattern);
            pattern.probability = Math.min(pattern.probability + 0.01, 1.0);
            window.controlledLog?.log(`📈 更新模式概率: ${matchedPattern} -> ${pattern.probability.toFixed(2)}`);
        }
    }
    
    /**
     * 查找匹配的模式
     */
    findMatchingPattern(sequence) {
        for (const [name, pattern] of this.patterns.entries()) {
            if (this.isSequenceMatch(sequence, pattern.sequence)) {
                return name;
            }
        }
        return null;
    }
    
    /**
     * 判断序列是否匹配
     */
    isSequenceMatch(userSequence, patternSequence) {
        if (userSequence.length < 2) {
            return false;
        }
        
        // 检查最后几个动作是否匹配模式的开始
        const lastActions = userSequence.slice(-Math.min(3, patternSequence.length));
        const patternStart = patternSequence.slice(0, lastActions.length);
        
        return lastActions.every((action, index) => action === patternStart[index]);
    }
    
    /**
     * 预测下一个状态
     */
    predictNextState(currentState, context = {}) {
        // 检查缓存
        const cacheKey = `${currentState}_${JSON.stringify(context)}`;
        if (this.predictionCache.has(cacheKey)) {
            const cached = this.predictionCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 5000) { // 5秒缓存
                return cached.prediction;
            }
        }
        
        // 查找相似的上下文
        const similarContexts = this.findSimilarContexts(context);
        
        // 计算预测
        const predictions = this.calculatePredictions(currentState, similarContexts);
        
        const prediction = {
            mostLikely: predictions[0] || { state: 'idle', confidence: 0.5 },
            alternatives: predictions.slice(1, 3),
            confidence: this.calculateConfidence(predictions),
            timestamp: Date.now()
        };
        
        // 缓存预测结果
        this.predictionCache.set(cacheKey, {
            prediction: prediction,
            timestamp: Date.now()
        });
        
        window.controlledLog?.log(`🔮 预测下一个状态: ${currentState} -> ${prediction.mostLikely.state} (${(prediction.confidence * 100).toFixed(1)}%)`);
        
        return prediction;
    }
    
    /**
     * 查找相似的上下文
     */
    findSimilarContexts(context) {
        return this.userBehavior.filter(behavior => {
            // 简单的相似度判断
            const contextKeys = Object.keys(context);
            const behaviorKeys = Object.keys(behavior.context);
            
            const commonKeys = contextKeys.filter(key => behaviorKeys.includes(key));
            
            return commonKeys.length > 0;
        });
    }
    
    /**
     * 计算预测
     */
    calculatePredictions(currentState, similarContexts) {
        const predictions = new Map();
        
        // 基于历史模式预测
        for (const [name, pattern] of this.patterns.entries()) {
            const currentIndex = pattern.sequence.indexOf(currentState);
            
            if (currentIndex >= 0 && currentIndex < pattern.sequence.length - 1) {
                const nextState = pattern.sequence[currentIndex + 1];
                const score = pattern.probability;
                
                if (!predictions.has(nextState) || predictions.get(nextState) < score) {
                    predictions.set(nextState, score);
                }
            }
        }
        
        // 基于相似上下文预测
        similarContexts.forEach(behavior => {
            if (behavior.outcome) {
                const score = 0.5; // 基础分数
                const existing = predictions.get(behavior.outcome) || 0;
                predictions.set(behavior.outcome, Math.max(existing, score));
            }
        });
        
        // 转换为数组并排序
        const sortedPredictions = Array.from(predictions.entries())
            .map(([state, confidence]) => ({ state, confidence }))
            .sort((a, b) => b.confidence - a.confidence);
        
        return sortedPredictions;
    }
    
    /**
     * 计算置信度
     */
    calculateConfidence(predictions) {
        if (predictions.length === 0) {
            return 0.5; // 默认置信度
        }
        
        // 使用最高预测的置信度
        return predictions[0].confidence;
    }
    
    /**
     * 获取优化建议
     */
    getOptimizationSuggestions(currentState) {
        const prediction = this.predictNextState(currentState);
        const suggestions = [];
        
        if (prediction.confidence > 0.7) {
            suggestions.push({
                type: 'preload',
                message: `可以预加载 ${prediction.mostLikely.state} 状态的资源`,
                confidence: prediction.confidence
            });
        }
        
        if (prediction.alternatives.length > 0) {
            suggestions.push({
                type: 'prepare',
                message: `准备备选状态: ${prediction.alternatives.map(a => a.state).join(', ')}`,
                confidence: prediction.confidence
            });
        }
        
        return suggestions;
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return {
            totalBehaviors: this.userBehavior.length,
            totalPatterns: this.patterns.size,
            cacheSize: this.predictionCache.size,
            recentBehaviors: this.userBehavior.slice(-5).map(b => b.action)
        };
    }
    
    /**
     * 清除历史
     */
    clearHistory() {
        this.userBehavior = [];
        this.predictionCache.clear();
        window.controlledLog?.log('🧹 预测历史已清除');
    }
}

// 全局实例
window.smartStatePredictor = null;

// 初始化函数
function initSmartStatePredictor() {
    if (window.smartStatePredictor) {
        window.smartStatePredictor.clearHistory();
    }
    
    window.smartStatePredictor = new SmartStatePredictor();
    window.controlledLog?.log('🔮 智能状态预测器已初始化');
    
    // 集成到状态同步管理器
    if (window.stateSyncManager) {
        window.stateSyncManager.addListener('voice_synthesis', (newState, oldState) => {
            window.smartStatePredictor.recordUserAction(newState, {
                previousState: oldState,
                timestamp: Date.now()
            });
        });
        
        window.controlledLog?.log('🔗 状态预测器已集成到状态同步管理器');
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmartStatePredictor);
} else {
    initSmartStatePredictor();
}

