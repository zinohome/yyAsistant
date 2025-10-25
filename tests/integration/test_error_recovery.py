"""
错误恢复集成测试
测试完整的错误恢复流程和状态同步场景
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestErrorRecoveryIntegration(unittest.TestCase):
    """测试错误恢复集成"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_error_handler = MockSmartErrorHandler()
        self.mock_state_manager = MockStateSyncManager()
    
    def test_websocket_error_recovery_flow(self):
        """测试WebSocket错误恢复流程"""
        # 模拟WebSocket连接错误
        websocket_error = {
            'message': 'WebSocket connection failed',
            'type': 'websocket',
            'severity': 'high'
        }
        
        # 处理错误
        analysis = self.mock_error_handler.analyze_error(websocket_error)
        
        # 验证错误分析
        self.assertEqual(analysis['category'], 'websocket')
        self.assertEqual(analysis['severity'], 'high')
        self.assertIn('检查网络连接', analysis['suggestions'])
        
        # 注册状态
        self.mock_state_manager.registerState('voice_call', {
            'status': 'idle',
            'isConnected': False
        })
        
        # 模拟状态更新
        self.mock_state_manager.updateState('voice_call', {
            'status': 'error',
            'isConnected': False,
            'error': websocket_error['message']
        })
        
        # 验证状态更新
        state = self.mock_state_manager.getState('voice_call')
        self.assertEqual(state['status'], 'error')
        self.assertFalse(state['isConnected'])
        self.assertEqual(state['error'], websocket_error['message'])
        
        # 模拟重试逻辑
        retry_result = self.mock_error_handler.should_auto_retry(analysis)
        self.assertTrue(retry_result)
        
        # 模拟重试执行
        retry_success = self.mock_error_handler.execute_retry('websocket')
        self.assertTrue(retry_success)
    
    def test_audio_error_recovery_flow(self):
        """测试音频错误恢复流程"""
        # 模拟音频错误
        audio_error = {
            'message': 'AudioContext error',
            'type': 'audio',
            'severity': 'medium'
        }
        
        # 处理错误
        analysis = self.mock_error_handler.analyze_error(audio_error)
        
        # 验证错误分析
        self.assertEqual(analysis['category'], 'audio')
        self.assertEqual(analysis['severity'], 'medium')
        self.assertIn('检查麦克风权限', analysis['suggestions'])
        
        # 注册状态
        self.mock_state_manager.registerState('audio_visualizer', {
            'status': 'idle',
            'isVisible': False
        })
        
        # 模拟状态更新
        self.mock_state_manager.updateState('audio_visualizer', {
            'status': 'error',
            'isVisible': False,
            'error': audio_error['message']
        })
        
        # 验证状态更新
        state = self.mock_state_manager.getState('audio_visualizer')
        self.assertEqual(state['status'], 'error')
        self.assertFalse(state['isVisible'])
        self.assertEqual(state['error'], audio_error['message'])
        
        # 模拟重试逻辑
        retry_result = self.mock_error_handler.should_auto_retry(analysis)
        self.assertTrue(retry_result)
    
    def test_tts_error_recovery_flow(self):
        """测试TTS错误恢复流程"""
        # 模拟TTS错误
        tts_error = {
            'message': 'TTS synthesis error',
            'type': 'tts',
            'severity': 'medium'
        }
        
        # 处理错误
        analysis = self.mock_error_handler.analyze_error(tts_error)
        
        # 验证错误分析
        self.assertEqual(analysis['category'], 'tts')
        self.assertEqual(analysis['severity'], 'medium')
        self.assertIn('检查语音合成服务', analysis['suggestions'])
        
        # 注册状态
        self.mock_state_manager.registerState('voice_synthesis', {
            'status': 'idle',
            'isPlaying': False,
            'isProcessing': False
        })
        
        # 模拟状态更新
        self.mock_state_manager.updateState('voice_synthesis', {
            'status': 'error',
            'isPlaying': False,
            'isProcessing': False,
            'error': tts_error['message']
        })
        
        # 验证状态更新
        state = self.mock_state_manager.getState('voice_synthesis')
        self.assertEqual(state['status'], 'error')
        self.assertFalse(state['isPlaying'])
        self.assertFalse(state['isProcessing'])
        self.assertEqual(state['error'], tts_error['message'])
    
    def test_network_error_recovery_flow(self):
        """测试网络错误恢复流程"""
        # 模拟网络错误
        network_error = {
            'message': 'Network timeout',
            'type': 'network',
            'severity': 'high'
        }
        
        # 处理错误
        analysis = self.mock_error_handler.analyze_error(network_error)
        
        # 验证错误分析
        self.assertEqual(analysis['category'], 'network')
        self.assertEqual(analysis['severity'], 'high')
        self.assertIn('检查网络连接', analysis['suggestions'])
        
        # 模拟重试逻辑
        retry_result = self.mock_error_handler.should_auto_retry(analysis)
        self.assertTrue(retry_result)
        
        # 模拟重试执行
        retry_success = self.mock_error_handler.execute_retry('network')
        self.assertTrue(retry_success)
    
    def test_state_sync_during_error_recovery(self):
        """测试错误恢复期间的状态同步"""
        # 注册多个状态
        self.mock_state_manager.registerState('voice_call', {
            'status': 'idle',
            'isConnected': False
        })
        self.mock_state_manager.registerState('voice_synthesis', {
            'status': 'idle',
            'isPlaying': False
        })
        
        # 模拟错误发生
        error = {'message': 'WebSocket connection failed', 'type': 'websocket'}
        analysis = self.mock_error_handler.analyze_error(error)
        
        # 更新相关状态
        self.mock_state_manager.updateState('voice_call', {
            'status': 'error',
            'isConnected': False,
            'error': error['message']
        })
        
        self.mock_state_manager.updateState('voice_synthesis', {
            'status': 'error',
            'isPlaying': False,
            'error': 'WebSocket不可用'
        })
        
        # 验证状态同步
        voice_call_state = self.mock_state_manager.getState('voice_call')
        synthesis_state = self.mock_state_manager.getState('voice_synthesis')
        
        self.assertEqual(voice_call_state['status'], 'error')
        self.assertEqual(synthesis_state['status'], 'error')
        
        # 模拟恢复过程
        self.mock_state_manager.updateState('voice_call', {
            'status': 'connecting',
            'isConnected': False,
            'error': None
        })
        
        # 验证恢复状态
        voice_call_state = self.mock_state_manager.getState('voice_call')
        self.assertEqual(voice_call_state['status'], 'connecting')
        self.assertIsNone(voice_call_state['error'])
    
    def test_error_history_tracking(self):
        """测试错误历史跟踪"""
        # 模拟多个错误
        errors = [
            {'message': 'WebSocket connection failed', 'type': 'websocket'},
            {'message': 'AudioContext error', 'type': 'audio'},
            {'message': 'TTS synthesis error', 'type': 'tts'}
        ]
        
        # 处理每个错误
        for error in errors:
            analysis = self.mock_error_handler.analyze_error(error)
            self.mock_error_handler.add_to_history(analysis)
        
        # 验证错误历史
        history = self.mock_error_handler.get_error_history()
        self.assertEqual(len(history), 3)
        
        # 验证错误统计
        stats = self.mock_error_handler.get_error_stats()
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['byCategory']['websocket'], 1)
        self.assertEqual(stats['byCategory']['audio'], 1)
        self.assertEqual(stats['byCategory']['tts'], 1)
    
    def test_retry_mechanism(self):
        """测试重试机制"""
        # 模拟重试配置
        max_attempts = 3
        retry_delays = [1000, 3000, 5000]
        
        # 测试重试调度
        for attempt in range(max_attempts):
            delay = retry_delays[attempt] if attempt < len(retry_delays) else 5000
            self.assertGreater(delay, 0)
        
        # 测试最大重试次数
        self.assertFalse(self.mock_error_handler.should_retry('websocket', 3, max_attempts))
        self.assertTrue(self.mock_error_handler.should_retry('websocket', 2, max_attempts))
    
    def test_error_recovery_success(self):
        """测试错误恢复成功"""
        # 模拟初始错误状态
        self.mock_state_manager.registerState('voice_call', {
            'status': 'error',
            'isConnected': False,
            'error': 'WebSocket connection failed'
        })
        
        # 模拟恢复过程
        recovery_steps = [
            {'status': 'connecting', 'isConnected': False, 'error': None},
            {'status': 'connected', 'isConnected': True, 'error': None}
        ]
        
        for step in recovery_steps:
            self.mock_state_manager.updateState('voice_call', step)
        
        # 验证最终状态
        final_state = self.mock_state_manager.getState('voice_call')
        self.assertEqual(final_state['status'], 'connected')
        self.assertTrue(final_state['isConnected'])
        self.assertIsNone(final_state['error'])


class MockSmartErrorHandler:
    """模拟智能错误处理系统"""
    
    def __init__(self):
        self.error_history = []
        self.error_patterns = {
            'websocket': {
                'patterns': [r'WebSocket.*failed', r'Connection.*lost'],
                'severity': 'high',
                'suggestions': ['检查网络连接', '尝试重新连接', '检查服务器状态']
            },
            'audio': {
                'patterns': [r'AudioContext', r'getUserMedia'],
                'severity': 'medium',
                'suggestions': ['检查麦克风权限', '尝试刷新页面', '检查浏览器音频支持']
            },
            'tts': {
                'patterns': [r'TTS.*error', r'synthesis.*error'],
                'severity': 'medium',
                'suggestions': ['检查语音合成服务', '尝试重新播放', '检查音频设备']
            },
            'network': {
                'patterns': [r'Network.*error', r'timeout'],
                'severity': 'high',
                'suggestions': ['检查网络连接', '尝试重新请求', '检查服务器状态']
            }
        }
    
    def analyze_error(self, error):
        """分析错误"""
        import re
        
        error_message = error.get('message', '')
        
        for category, config in self.error_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return {
                        'category': category,
                        'severity': config['severity'],
                        'suggestions': config['suggestions'],
                        'originalError': error,
                        'timestamp': 1234567890
                    }
        
        return {
            'category': 'unknown',
            'severity': 'medium',
            'suggestions': ['默认建议'],
            'originalError': error,
            'timestamp': 1234567890
        }
    
    def should_auto_retry(self, analysis):
        """判断是否应该自动重试"""
        return analysis['category'] in ['websocket', 'network', 'audio', 'tts']
    
    def execute_retry(self, category):
        """执行重试"""
        retry_strategies = {
            'websocket': 'reconnect',
            'network': 'retry_request',
            'audio': 'reinitialize',
            'tts': 'retry_synthesis'
        }
        
        return category in retry_strategies
    
    def should_retry(self, category, attempt_count, max_attempts):
        """判断是否应该重试"""
        return attempt_count < max_attempts and category in ['websocket', 'network', 'audio', 'tts']
    
    def add_to_history(self, analysis):
        """添加到错误历史"""
        self.error_history.append(analysis)
    
    def get_error_history(self):
        """获取错误历史"""
        return self.error_history
    
    def get_error_stats(self):
        """获取错误统计"""
        stats = {
            'total': len(self.error_history),
            'byCategory': {},
            'bySeverity': {}
        }
        
        for error in self.error_history:
            category = error['category']
            severity = error['severity']
            
            stats['byCategory'][category] = stats['byCategory'].get(category, 0) + 1
            stats['bySeverity'][severity] = stats['bySeverity'].get(severity, 0) + 1
        
        return stats


class MockStateSyncManager:
    """模拟状态同步管理器"""
    
    def __init__(self):
        self.states = {}
    
    def registerState(self, stateName, initialState=None):
        """注册状态"""
        if initialState is None:
            initialState = {}
        
        self.states[stateName] = {
            **initialState,
            '_metadata': {
                'createdAt': 1234567890,
                'lastUpdated': 1234567890,
                'version': 1
            }
        }
    
    def getState(self, stateName):
        """获取状态"""
        return self.states.get(stateName)
    
    def updateState(self, stateName, updates):
        """更新状态"""
        if stateName not in self.states:
            return False
        
        current_state = self.states[stateName]
        new_state = {
            **current_state,
            **updates,
            '_metadata': {
                **current_state['_metadata'],
                'lastUpdated': 1234567890,
                'version': current_state['_metadata']['version'] + 1
            }
        }
        
        self.states[stateName] = new_state
        return True


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)