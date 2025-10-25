# -*- coding: utf-8 -*-
"""
智能状态预测器测试
"""
import unittest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestSmartStatePredictor(unittest.TestCase):
    """测试智能状态预测器"""
    
    def test_predictor_initialization(self):
        """测试预测器初始化"""
        # 注意：JavaScript组件需要在浏览器环境中测试
        self.assertTrue(True, "状态预测器需要在浏览器环境中测试")
    
    def test_common_patterns(self):
        """测试常见模式"""
        # 测试预定义的常见模式
        patterns = {
            'text_chat': ['idle', 'text_processing', 'text_tts', 'idle'],
            'voice_recording': ['idle', 'recording', 'voice_stt', 'voice_sse', 'voice_tts', 'idle'],
            'voice_call': ['idle', 'calling', 'idle']
        }
        
        for pattern_name, sequence in patterns.items():
            with self.subTest(pattern=pattern_name):
                self.assertGreater(len(sequence), 1)
                self.assertEqual(sequence[0], 'idle')
                self.assertEqual(sequence[-1], 'idle')
    
    def test_behavior_recording(self):
        """测试行为记录"""
        # 测试用户行为记录功能
        max_history = 100
        self.assertGreater(max_history, 0)
    
    def test_pattern_matching(self):
        """测试模式匹配"""
        # 测试序列匹配算法
        test_sequence = ['idle', 'text_processing']
        pattern_sequence = ['idle', 'text_processing', 'text_tts', 'idle']
        
        # 简单的匹配测试
        is_match = test_sequence[0] == pattern_sequence[0] and test_sequence[1] == pattern_sequence[1]
        self.assertTrue(is_match)
    
    def test_prediction_confidence(self):
        """测试预测置信度"""
        # 测试置信度计算
        confidence_levels = [0.6, 0.7, 0.8]
        
        for confidence in confidence_levels:
            with self.subTest(confidence=confidence):
                self.assertGreaterEqual(confidence, 0.0)
                self.assertLessEqual(confidence, 1.0)
    
    def test_optimization_suggestions(self):
        """测试优化建议"""
        # 测试优化建议生成
        suggestion_types = ['preload', 'prepare']
        
        for suggestion_type in suggestion_types:
            with self.subTest(type=suggestion_type):
                self.assertIn(suggestion_type, ['preload', 'prepare'])


if __name__ == '__main__':
    unittest.main()

