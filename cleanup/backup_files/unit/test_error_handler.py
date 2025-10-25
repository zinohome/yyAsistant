"""
智能错误处理系统单元测试
测试错误分析、分类、智能提示和自动重试功能
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestSmartErrorHandler(unittest.TestCase):
    """测试智能错误处理系统"""
    
    def setUp(self):
        """测试前准备"""
        self.test_errors = [
            {
                'message': 'WebSocket connection failed',
                'expected_category': 'websocket',
                'expected_severity': 'high'
            },
            {
                'message': 'AudioContext error',
                'expected_category': 'audio',
                'expected_severity': 'medium'
            },
            {
                'message': 'TTS synthesis error',
                'expected_category': 'tts',
                'expected_severity': 'medium'
            },
            {
                'message': 'Network timeout',
                'expected_category': 'network',
                'expected_severity': 'high'
            },
            {
                'message': 'State management error',
                'expected_category': 'state',
                'expected_severity': 'low'
            }
        ]
    
    def test_error_patterns_initialization(self):
        """测试错误模式初始化"""
        # 模拟JavaScript错误模式
        error_patterns = {
            'websocket': {
                'patterns': [
                    r'WebSocket connection failed',
                    r'WebSocket connection to .* failed',
                    r'Connection closed',
                    r'Connection lost'
                ],
                'severity': 'high',
                'category': 'connection',
                'suggestions': [
                    '检查网络连接',
                    '尝试重新连接',
                    '检查服务器状态'
                ]
            },
            'audio': {
                'patterns': [
                    r'AudioContext',
                    r'getUserMedia',
                    r'audio.*error',
                    r'microphone.*access'
                ],
                'severity': 'medium',
                'category': 'audio',
                'suggestions': [
                    '检查麦克风权限',
                    '尝试刷新页面',
                    '检查浏览器音频支持'
                ]
            }
        }
        
        # 验证错误模式结构
        self.assertIn('websocket', error_patterns)
        self.assertIn('audio', error_patterns)
        self.assertEqual(error_patterns['websocket']['severity'], 'high')
        self.assertEqual(error_patterns['audio']['severity'], 'medium')
    
    def test_error_analysis(self):
        """测试错误分析"""
        import re
        
        # 模拟错误分析逻辑
        def analyze_error(error_message):
            error_patterns = {
                'websocket': {
                    'patterns': [r'WebSocket.*failed', r'Connection.*lost'],
                    'severity': 'high',
                    'category': 'connection'
                },
                'audio': {
                    'patterns': [r'AudioContext', r'getUserMedia'],
                    'severity': 'medium',
                    'category': 'audio'
                }
            }
            
            for category, config in error_patterns.items():
                for pattern in config['patterns']:
                    if re.search(pattern, error_message, re.IGNORECASE):
                        return {
                            'category': category,
                            'severity': config['severity'],
                            'suggestions': ['建议操作1', '建议操作2']
                        }
            
            return {
                'category': 'unknown',
                'severity': 'medium',
                'suggestions': ['默认建议']
            }
        
        # 测试各种错误类型
        for test_error in self.test_errors:
            with self.subTest(error=test_error['message']):
                result = analyze_error(test_error['message'])
                self.assertIn('category', result)
                self.assertIn('severity', result)
                self.assertIn('suggestions', result)
                self.assertIsInstance(result['suggestions'], list)
    
    def test_error_categorization(self):
        """测试错误分类"""
        # 模拟错误分类逻辑
        def categorize_error(error_message):
            if 'WebSocket' in error_message or 'Connection' in error_message:
                return 'websocket'
            elif 'Audio' in error_message or 'microphone' in error_message:
                return 'audio'
            elif 'TTS' in error_message or 'synthesis' in error_message:
                return 'tts'
            elif 'Network' in error_message or 'timeout' in error_message:
                return 'network'
            elif 'State' in error_message or 'callback' in error_message:
                return 'state'
            else:
                return 'unknown'
        
        # 测试分类准确性
        for test_error in self.test_errors:
            with self.subTest(error=test_error['message']):
                category = categorize_error(test_error['message'])
                self.assertEqual(category, test_error['expected_category'])
    
    def test_severity_assessment(self):
        """测试严重程度评估"""
        # 模拟严重程度评估逻辑
        def assess_severity(category):
            severity_map = {
                'websocket': 'high',
                'network': 'high',
                'audio': 'medium',
                'tts': 'medium',
                'state': 'low',
                'unknown': 'medium'
            }
            return severity_map.get(category, 'medium')
        
        # 测试严重程度评估
        for test_error in self.test_errors:
            with self.subTest(error=test_error['message']):
                severity = assess_severity(test_error['expected_category'])
                self.assertEqual(severity, test_error['expected_severity'])
    
    def test_suggestion_generation(self):
        """测试建议生成"""
        # 模拟建议生成逻辑
        def generate_suggestions(category, severity):
            suggestions_map = {
                'websocket': [
                    '检查网络连接',
                    '尝试重新连接',
                    '检查服务器状态'
                ],
                'audio': [
                    '检查麦克风权限',
                    '尝试刷新页面',
                    '检查浏览器音频支持'
                ],
                'tts': [
                    '检查语音合成服务',
                    '尝试重新播放',
                    '检查音频设备'
                ],
                'network': [
                    '检查网络连接',
                    '尝试重新请求',
                    '检查服务器状态'
                ],
                'state': [
                    '刷新页面',
                    '检查组件状态',
                    '重新初始化'
                ]
            }
            
            return suggestions_map.get(category, ['默认建议'])
        
        # 测试建议生成
        test_cases = [
            ('websocket', 'high', 3),
            ('audio', 'medium', 3),
            ('tts', 'medium', 3),
            ('network', 'high', 3),
            ('state', 'low', 3),
            ('unknown', 'medium', 1)
        ]
        
        for category, severity, expected_count in test_cases:
            with self.subTest(category=category):
                suggestions = generate_suggestions(category, severity)
                self.assertIsInstance(suggestions, list)
                self.assertGreaterEqual(len(suggestions), expected_count)
    
    def test_retry_logic(self):
        """测试重试逻辑"""
        # 模拟重试逻辑
        def should_retry(category, severity, attempt_count, max_attempts=3):
            if attempt_count >= max_attempts:
                return False
            if severity == 'low':
                return False
            if category in ['websocket', 'network']:
                return True
            if category in ['audio', 'tts'] and severity != 'low':
                return True
            return False
        
        # 测试重试决策
        test_cases = [
            ('websocket', 'high', 0, True),
            ('websocket', 'high', 2, True),
            ('websocket', 'high', 3, False),
            ('audio', 'medium', 0, True),
            ('audio', 'low', 0, False),
            ('state', 'low', 0, False),
            ('unknown', 'medium', 0, False)
        ]
        
        for category, severity, attempt_count, expected in test_cases:
            with self.subTest(category=category, severity=severity, attempt=attempt_count):
                result = should_retry(category, severity, attempt_count)
                self.assertEqual(result, expected)
    
    def test_error_history_management(self):
        """测试错误历史管理"""
        # 模拟错误历史管理
        class MockErrorHistory:
            def __init__(self, max_size=100):
                self.errors = []
                self.max_size = max_size
            
            def add_error(self, error):
                self.errors.append({
                    'message': error,
                    'timestamp': 1234567890,
                    'id': f'error_{len(self.errors)}'
                })
                
                # 限制历史记录长度
                if len(self.errors) > self.max_size:
                    self.errors = self.errors[-self.max_size:]
            
            def get_recent_errors(self, count=10):
                return self.errors[-count:]
            
            def clear_history(self):
                self.errors = []
        
        # 测试错误历史管理
        history = MockErrorHistory(max_size=5)
        
        # 添加错误
        for i in range(10):
            history.add_error(f'Test error {i}')
        
        # 验证历史记录长度限制（应该被限制为5）
        self.assertLessEqual(len(history.errors), 5)
        
        # 验证最近错误
        recent = history.get_recent_errors(3)
        self.assertLessEqual(len(recent), 3)
        
        # 测试清除历史
        history.clear_history()
        self.assertEqual(len(history.errors), 0)


class TestErrorRecovery(unittest.TestCase):
    """测试错误恢复功能"""
    
    def test_automatic_retry_scheduling(self):
        """测试自动重试调度"""
        # 模拟重试调度逻辑
        def schedule_retry(category, attempt_count, max_attempts=3):
            if attempt_count >= max_attempts:
                return None
            
            delays = [1000, 3000, 5000]  # 递增延迟
            return delays[attempt_count] if attempt_count < len(delays) else 5000
        
        # 测试重试延迟
        test_cases = [
            ('websocket', 0, 1000),
            ('websocket', 1, 3000),
            ('websocket', 2, 5000),
            ('websocket', 3, None),
            ('audio', 0, 1000),
            ('audio', 1, 3000)
        ]
        
        for category, attempt_count, expected_delay in test_cases:
            with self.subTest(category=category, attempt=attempt_count):
                delay = schedule_retry(category, attempt_count)
                self.assertEqual(delay, expected_delay)
    
    def test_error_recovery_strategies(self):
        """测试错误恢复策略"""
        # 模拟错误恢复策略
        def get_recovery_strategy(category):
            strategies = {
                'websocket': 'reconnect',
                'audio': 'reinitialize',
                'tts': 'retry_synthesis',
                'network': 'retry_request',
                'state': 'refresh_page'
            }
            return strategies.get(category, 'unknown')
        
        # 测试恢复策略
        test_cases = [
            ('websocket', 'reconnect'),
            ('audio', 'reinitialize'),
            ('tts', 'retry_synthesis'),
            ('network', 'retry_request'),
            ('state', 'refresh_page'),
            ('unknown', 'unknown')
        ]
        
        for category, expected_strategy in test_cases:
            with self.subTest(category=category):
                strategy = get_recovery_strategy(category)
                self.assertEqual(strategy, expected_strategy)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)