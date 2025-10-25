"""
UI优化第一阶段集成测试
测试音频可视化器、播放状态指示器和消息操作栏的集成
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from components.smart_message_actions import create_smart_message_actions


class TestUIIntegration(unittest.TestCase):
    """测试UI组件集成"""
    
    def setUp(self):
        """测试前准备"""
        self.message_id = "integration_test_123"
    
    def test_audio_visualizer_integration(self):
        """测试音频可视化器集成"""
        # 验证enhanced_audio_visualizer.js文件存在
        visualizer_path = os.path.join(project_root, 'assets', 'js', 'enhanced_audio_visualizer.js')
        self.assertTrue(os.path.exists(visualizer_path), "enhanced_audio_visualizer.js文件不存在")
        
        # 验证文件内容包含必要的类和方法
        with open(visualizer_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('EnhancedAudioVisualizer', content, "缺少EnhancedAudioVisualizer类")
            self.assertIn('updateState', content, "缺少updateState方法")
            self.assertIn('startAnimation', content, "缺少startAnimation方法")
    
    def test_playback_status_integration(self):
        """测试播放状态指示器集成"""
        # 验证enhanced_playback_status.js文件存在
        status_path = os.path.join(project_root, 'assets', 'js', 'enhanced_playback_status.js')
        self.assertTrue(os.path.exists(status_path), "enhanced_playback_status.js文件不存在")
        
        # 验证文件内容包含必要的类和方法
        with open(status_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('EnhancedPlaybackStatus', content, "缺少EnhancedPlaybackStatus类")
            self.assertIn('showStatus', content, "缺少showStatus方法")
            self.assertIn('hide', content, "缺少hide方法")
    
    def test_smart_message_actions_integration(self):
        """测试智能消息操作栏集成"""
        # 验证smart_message_actions.py文件存在
        actions_path = os.path.join(project_root, 'components', 'smart_message_actions.py')
        self.assertTrue(os.path.exists(actions_path), "smart_message_actions.py文件不存在")
        
        # 测试不同状态下的操作栏创建
        test_cases = [
            {'state': 'SUCCESS', 'streaming': False},
            {'state': 'PROCESSING', 'streaming': True},
            {'state': 'ERROR', 'streaming': False, 'error_info': '测试错误'}
        ]
        
        for case in test_cases:
            with self.subTest(state=case['state']):
                actions = create_smart_message_actions(
                    message_id=self.message_id,
                    current_state=case['state'],
                    is_streaming=case.get('streaming', False),
                    error_info=case.get('error_info')
                )
                self.assertIsNotNone(actions, f"状态{case['state']}的操作栏创建失败")
    
    def test_voice_websocket_manager_integration(self):
        """测试语音WebSocket管理器集成"""
        # 验证voice_websocket_manager.js文件存在
        manager_path = os.path.join(project_root, 'assets', 'js', 'voice_websocket_manager.js')
        self.assertTrue(os.path.exists(manager_path), "voice_websocket_manager.js文件不存在")
        
        # 验证文件内容包含增强音频可视化器的集成
        with open(manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('enhancedAudioVisualizer', content, "缺少enhancedAudioVisualizer集成")
            self.assertIn('updateState', content, "缺少updateState调用")
    
    def test_voice_player_enhanced_integration(self):
        """测试增强语音播放器集成"""
        # 验证voice_player_enhanced.js文件存在
        player_path = os.path.join(project_root, 'assets', 'js', 'voice_player_enhanced.js')
        self.assertTrue(os.path.exists(player_path), "voice_player_enhanced.js文件不存在")
        
        # 验证文件内容包含增强播放状态指示器的集成
        with open(player_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('enhancedPlaybackStatus', content, "缺少enhancedPlaybackStatus集成")
            self.assertIn('initEnhancedPlaybackStatus', content, "缺少initEnhancedPlaybackStatus方法")
    
    def test_chat_agent_message_integration(self):
        """测试聊天代理消息组件集成"""
        # 验证chat_agent_message.py文件存在
        message_path = os.path.join(project_root, 'components', 'chat_agent_message.py')
        self.assertTrue(os.path.exists(message_path), "chat_agent_message.py文件不存在")
        
        # 验证文件内容包含智能消息操作栏的导入
        with open(message_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('smart_message_actions', content, "缺少smart_message_actions导入")
            self.assertIn('create_smart_message_actions', content, "缺少create_smart_message_actions调用")
    
    def test_layout_integration(self):
        """测试布局文件集成"""
        # 验证chat.py文件存在
        layout_path = os.path.join(project_root, 'views', 'core_pages', 'chat.py')
        self.assertTrue(os.path.exists(layout_path), "chat.py文件不存在")
        
        # 验证文件内容包含新的JavaScript文件引用
        with open(layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('enhanced_audio_visualizer.js', content, "缺少enhanced_audio_visualizer.js引用")
            self.assertIn('enhanced_playback_status.js', content, "缺少enhanced_playback_status.js引用")
    
    def test_core_buttons_preserved(self):
        """测试核心按钮保留"""
        # 验证智能消息操作栏保留了原有的核心按钮
        actions = create_smart_message_actions(
            message_id=self.message_id,
            current_state='SUCCESS'
        )
        
        # 验证返回的组件结构正确
        self.assertIsNotNone(actions)
        self.assertTrue(hasattr(actions, 'children'))
        
        # 验证包含核心按钮的ID
        actions_str = str(actions)
        self.assertIn('ai-chat-x-regenerate', actions_str, "缺少重新生成按钮")
        self.assertIn('ai-chat-x-copy', actions_str, "缺少复制按钮")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)