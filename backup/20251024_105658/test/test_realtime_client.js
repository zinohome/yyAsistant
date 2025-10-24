/**
 * 实时语音客户端测试
 */

describe('RealtimeAPIClient', () => {
    let client;
    
    beforeEach(() => {
        client = new RealtimeAPIClient();
    });
    
    afterEach(() => {
        if (client) {
            client.disconnect();
        }
    });
    
    test('should create client instance', () => {
        expect(client).toBeDefined();
        expect(client.isConnected).toBe(false);
        expect(client.token).toBeNull();
    });
    
    test('should have correct default values', () => {
        expect(client.model).toBe('gpt-4o-realtime-preview-2024-10-01');
        expect(client.reconnectAttempts).toBe(0);
        expect(client.maxReconnectAttempts).toBe(3);
        expect(client.reconnectDelay).toBe(1000);
    });
    
    test('should handle event listeners', () => {
        const handler = jest.fn();
        
        client.on('test_event', handler);
        client.emit('test_event', { data: 'test' });
        
        expect(handler).toHaveBeenCalledWith({ data: 'test' });
    });
    
    test('should remove event listeners', () => {
        const handler = jest.fn();
        
        client.on('test_event', handler);
        client.off('test_event', handler);
        client.emit('test_event', { data: 'test' });
        
        expect(handler).not.toHaveBeenCalled();
    });
    
    test('should get API key', () => {
        const apiKey = client.getApiKey();
        expect(apiKey).toBeDefined();
        expect(typeof apiKey).toBe('string');
    });
    
    test('should handle message sending when not connected', () => {
        expect(() => {
            client.sendMessage({ type: 'test' });
        }).toThrow('WebSocket未连接');
    });
    
    test('should handle disconnect', () => {
        client.disconnect();
        expect(client.isConnected).toBe(false);
        expect(client.ws).toBeNull();
    });
});

describe('RealtimeAudioProcessor', () => {
    let processor;
    
    beforeEach(() => {
        processor = new RealtimeAudioProcessor();
    });
    
    afterEach(() => {
        if (processor) {
            processor.cleanup();
        }
    });
    
    test('should create processor instance', () => {
        expect(processor).toBeDefined();
        expect(processor.isCapturing).toBe(false);
        expect(processor.sampleRate).toBe(24000);
        expect(processor.channelCount).toBe(1);
    });
    
    test('should have correct default values', () => {
        expect(processor.speechThreshold).toBe(0.01);
        expect(processor.silenceDuration).toBe(1000);
        expect(processor.isSpeaking).toBe(false);
    });
    
    test('should check browser support', () => {
        const isSupported = RealtimeAudioProcessor.isSupported();
        expect(typeof isSupported).toBe('boolean');
    });
    
    test('should get supported formats', () => {
        const formats = RealtimeAudioProcessor.getSupportedFormats();
        expect(formats).toBeDefined();
        expect(formats.sampleRate).toBeDefined();
        expect(formats.channelCount).toBeDefined();
        expect(formats.echoCancellation).toBe(true);
    });
    
    test('should set callbacks', () => {
        const visualizationCallback = jest.fn();
        const speechCallback = jest.fn();
        
        processor.setVisualizationCallback(visualizationCallback);
        processor.setSpeechDetectionCallback(speechCallback);
        
        expect(processor.visualizationCallback).toBe(visualizationCallback);
        expect(processor.speechDetectionCallback).toBe(speechCallback);
    });
    
    test('should set thresholds', () => {
        processor.setSpeechThreshold(0.05);
        processor.setSilenceDuration(2000);
        
        expect(processor.speechThreshold).toBe(0.05);
        expect(processor.silenceDuration).toBe(2000);
    });
    
    test('should handle cleanup', () => {
        processor.cleanup();
        expect(processor.isCapturing).toBe(false);
        expect(processor.visualizationCallback).toBeNull();
        expect(processor.speechDetectionCallback).toBeNull();
    });
});

describe('RealtimeAdapterClient', () => {
    let client;
    
    beforeEach(() => {
        client = new RealtimeAdapterClient('http://localhost:9800');
    });
    
    test('should create client instance', () => {
        expect(client).toBeDefined();
        expect(client.backendUrl).toBe('http://localhost:9800');
        expect(client.apiKey).toBeDefined();
    });
    
    test('should have correct default headers', () => {
        expect(client.defaultHeaders).toBeDefined();
        expect(client.defaultHeaders['Content-Type']).toBe('application/json');
        expect(client.defaultHeaders['Authorization']).toContain('Bearer');
    });
    
    test('should set backend URL', () => {
        client.setBackendUrl('https://api.example.com');
        expect(client.backendUrl).toBe('https://api.example.com');
    });
    
    test('should set API key', () => {
        const newApiKey = 'new-api-key';
        client.setApiKey(newApiKey);
        expect(client.apiKey).toBe(newApiKey);
        expect(client.defaultHeaders['Authorization']).toBe(`Bearer ${newApiKey}`);
    });
    
    test('should get API key', () => {
        const apiKey = client.getApiKey();
        expect(apiKey).toBeDefined();
        expect(typeof apiKey).toBe('string');
    });
    
    test('should handle error responses', () => {
        const mockResponse = {
            ok: false,
            status: 401,
            statusText: 'Unauthorized'
        };
        
        expect(() => {
            client.handleErrorResponse(mockResponse, '测试操作');
        }).toThrow('认证失败，请检查API密钥');
    });
    
    test('should handle different error status codes', () => {
        const testCases = [
            { status: 403, expected: '访问被拒绝，请检查权限' },
            { status: 404, expected: 'API端点不存在' },
            { status: 500, expected: '服务器内部错误' }
        ];
        
        testCases.forEach(({ status, expected }) => {
            const mockResponse = {
                ok: false,
                status: status,
                statusText: 'Error'
            };
            
            expect(() => {
                client.handleErrorResponse(mockResponse, '测试操作');
            }).toThrow(expected);
        });
    });
    
    test('should handle retry mechanism', async () => {
        let attemptCount = 0;
        const requestFn = jest.fn().mockImplementation(() => {
            attemptCount++;
            if (attemptCount < 2) {
                throw new Error('Network error');
            }
            return Promise.resolve('success');
        });
        
        const result = await client.retryRequest(requestFn, 3, 10);
        
        expect(result).toBe('success');
        expect(attemptCount).toBe(2);
        expect(requestFn).toHaveBeenCalledTimes(2);
    });
    
    test('should throw error after max retries', async () => {
        const requestFn = jest.fn().mockRejectedValue(new Error('Network error'));
        
        await expect(client.retryRequest(requestFn, 2, 10)).rejects.toThrow('Network error');
        expect(requestFn).toHaveBeenCalledTimes(2);
    });
});
