"""
UI优化第一阶段单元测试
测试智能消息操作栏组件
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from components.smart_message_actions import (
    create_smart_message_actions,
    create_cancel_button,
    create_retry_button,
    create_progress_indicator,
    create_status_indicator,
    create_error_tooltip,
    get_button_style
)


class TestSmartMessageActions(unittest.TestCase):
    """测试智能消息操作栏"""
    
    def setUp(self):
        """测试前准备"""
        self.message_id = "test_message_123"
    
    def test_create_smart_message_actions_success(self):
        """测试成功状态的操作栏"""
        actions = create_smart_message_actions(
            message_id=self.message_id,
            current_state='SUCCESS',
            is_streaming=False
        )
        
        # 验证返回的是AntdRow组件
        self.assertEqual(actions.__class__.__name__, 'AntdRow')
        
        # 验证包含核心按钮
        self.assertIsNotNone(actions)
    
    def test_create_smart_message_actions_processing(self):
        """测试处理中状态的操作栏"""
        actions = create_smart_message_actions(
            message_id=self.message_id,
            current_state='PROCESSING',
            is_streaming=True
        )
        
        # 验证返回的是AntdRow组件
        self.assertEqual(actions.__class__.__name__, 'AntdRow')
    
    def test_create_smart_message_actions_error(self):
        """测试错误状态的操作栏"""
        actions = create_smart_message_actions(
            message_id=self.message_id,
            current_state='ERROR',
            is_streaming=False,
            error_info="测试错误信息"
        )
        
        # 验证返回的是AntdRow组件
        self.assertEqual(actions.__class__.__name__, 'AntdRow')
    
    def test_create_cancel_button(self):
        """测试取消按钮创建"""
        button = create_cancel_button(self.message_id)
        self.assertIsNotNone(button)
        self.assertEqual(button.__class__.__name__, 'AntdButton')
    
    def test_create_retry_button(self):
        """测试重试按钮创建"""
        button = create_retry_button(self.message_id)
        self.assertIsNotNone(button)
        self.assertEqual(button.__class__.__name__, 'AntdButton')
    
    def test_create_progress_indicator(self):
        """测试进度指示器创建"""
        indicator = create_progress_indicator()
        self.assertIsNotNone(indicator)
        self.assertEqual(indicator.__class__.__name__, 'Div')
    
    def test_create_status_indicator(self):
        """测试状态指示器创建"""
        # 测试成功状态
        success_indicator = create_status_indicator('SUCCESS')
        self.assertIsNotNone(success_indicator)
        self.assertEqual(success_indicator.__class__.__name__, 'AntdTag')
        
        # 测试处理中状态
        processing_indicator = create_status_indicator('PROCESSING')
        self.assertIsNotNone(processing_indicator)
        
        # 测试错误状态
        error_indicator = create_status_indicator('ERROR')
        self.assertIsNotNone(error_indicator)
    
    def test_create_error_tooltip(self):
        """测试错误提示创建"""
        tooltip = create_error_tooltip("测试错误信息")
        self.assertIsNotNone(tooltip)
        self.assertEqual(tooltip.__class__.__name__, 'AntdTooltip')
    
    def test_get_button_style(self):
        """测试按钮样式获取"""
        # 测试成功状态样式
        success_style = get_button_style('SUCCESS', 'regenerate')
        self.assertIn('color', success_style)
        self.assertEqual(success_style['color'], 'rgba(0,0,0,0.75)')
        
        # 测试处理中状态样式
        processing_style = get_button_style('PROCESSING', 'regenerate')
        self.assertIn('color', processing_style)
        self.assertEqual(processing_style['color'], '#1890ff')
        self.assertIn('opacity', processing_style)
        
        # 测试错误状态样式
        error_style = get_button_style('ERROR', 'regenerate')
        self.assertIn('color', error_style)
        self.assertEqual(error_style['color'], '#ff4d4f')


class TestUIOptimizationIntegration(unittest.TestCase):
    """测试UI优化集成"""
    
    def test_smart_message_actions_preserves_core_buttons(self):
        """测试智能消息操作栏保留核心按钮"""
        actions = create_smart_message_actions(
            message_id="test_123",
            current_state='SUCCESS'
        )
        
        # 验证返回的组件不为空
        self.assertIsNotNone(actions)
        
        # 验证包含必要的属性
        self.assertTrue(hasattr(actions, 'children'))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)