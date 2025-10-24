/**
 * 实时语音适配器通信客户端
 * 处理与后端适配器API的通信
 */

class RealtimeAdapterClient {
    constructor(backendUrl = '') {
        this.backendUrl = backendUrl;
        this.apiKey = this.getApiKey();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
        };
    }
    
    /**
     * 获取记忆
     */
    async getMemory(conversationId, query) {
        try {
            console.log('获取记忆:', conversationId, query);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/memory`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    conversation_id: conversationId,
                    query: query
                })
            });
            
            if (!response.ok) {
                throw new Error(`获取记忆失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`获取记忆失败: ${data.error || '未知错误'}`);
            }
            
            console.log('记忆获取成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('获取记忆失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取人格配置
     */
    async getPersonality(personalityId) {
        try {
            console.log('获取人格配置:', personalityId);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/personality`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    personality_id: personalityId
                })
            });
            
            if (!response.ok) {
                throw new Error(`获取人格配置失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`获取人格配置失败: ${data.error || '未知错误'}`);
            }
            
            console.log('人格配置获取成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('获取人格配置失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取工具列表
     */
    async getTools(personalityId = null) {
        try {
            console.log('获取工具列表:', personalityId);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/tools`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    personality_id: personalityId
                })
            });
            
            if (!response.ok) {
                throw new Error(`获取工具列表失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`获取工具列表失败: ${data.error || '未知错误'}`);
            }
            
            console.log('工具列表获取成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('获取工具列表失败:', error);
            throw error;
        }
    }
    
    /**
     * 执行工具
     */
    async executeTool(toolName, parameters) {
        try {
            console.log('执行工具:', toolName, parameters);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/tools/execute`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    tool_name: toolName,
                    parameters: parameters
                })
            });
            
            if (!response.ok) {
                throw new Error(`执行工具失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`执行工具失败: ${data.error || '未知错误'}`);
            }
            
            console.log('工具执行成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('执行工具失败:', error);
            throw error;
        }
    }
    
    /**
     * 保存记忆
     */
    async saveMemory(conversationId, content, metadata = null) {
        try {
            console.log('保存记忆:', conversationId, content);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/memory/save`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    conversation_id: conversationId,
                    content: content,
                    metadata: metadata
                })
            });
            
            if (!response.ok) {
                throw new Error(`保存记忆失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`保存记忆失败: ${data.error || '未知错误'}`);
            }
            
            console.log('记忆保存成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('保存记忆失败:', error);
            throw error;
        }
    }
    
    /**
     * 创建实时语音会话
     */
    async createSession(conversationId, personalityId = null, sessionConfig = null) {
        try {
            console.log('创建实时语音会话:', conversationId, personalityId);
            
            const response = await fetch(`${this.backendUrl}/v1/realtime/session`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    conversation_id: conversationId,
                    personality_id: personalityId,
                    session_config: sessionConfig
                })
            });
            
            if (!response.ok) {
                throw new Error(`创建会话失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`创建会话失败: ${data.error || '未知错误'}`);
            }
            
            console.log('会话创建成功:', data.data);
            return data.data;
            
        } catch (error) {
            console.error('创建会话失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取API密钥
     */
    getApiKey() {
        // 从全局配置或环境变量获取API密钥
        return window.voiceConfig?.API_KEY || 'yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4';
    }
    
    /**
     * 设置后端URL
     */
    setBackendUrl(url) {
        this.backendUrl = url;
    }
    
    /**
     * 设置API密钥
     */
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        this.defaultHeaders['Authorization'] = `Bearer ${apiKey}`;
    }
    
    /**
     * 检查连接状态
     */
    async checkConnection() {
        try {
            const response = await fetch(`${this.backendUrl}/v1/realtime/session`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify({
                    conversation_id: 'test_connection'
                })
            });
            
            return response.ok;
            
        } catch (error) {
            console.error('检查连接失败:', error);
            return false;
        }
    }
    
    /**
     * 处理错误响应
     */
    handleErrorResponse(response, operation) {
        if (!response.ok) {
            const status = response.status;
            const statusText = response.statusText;
            
            let errorMessage = `${operation}失败: ${status} ${statusText}`;
            
            if (status === 401) {
                errorMessage = '认证失败，请检查API密钥';
            } else if (status === 403) {
                errorMessage = '访问被拒绝，请检查权限';
            } else if (status === 404) {
                errorMessage = 'API端点不存在';
            } else if (status === 500) {
                errorMessage = '服务器内部错误';
            }
            
            throw new Error(errorMessage);
        }
    }
    
    /**
     * 重试机制
     */
    async retryRequest(requestFn, maxRetries = 3, delay = 1000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await requestFn();
            } catch (error) {
                if (i === maxRetries - 1) {
                    throw error;
                }
                
                console.log(`请求失败，${delay}ms后重试 (${i + 1}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2; // 指数退避
            }
        }
    }
}

// 导出类
window.RealtimeAdapterClient = RealtimeAdapterClient;
