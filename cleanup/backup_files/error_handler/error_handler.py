"""
错误处理模块

提供统一的错误处理功能，包括错误分类、错误处理、错误恢复等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import time
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型枚举"""
    WEBSOCKET_CONNECTION = 'websocket_connection'  # WebSocket连接错误
    WEBSOCKET_MESSAGE = 'websocket_message'        # WebSocket消息错误
    STATE_TRANSITION = 'state_transition'          # 状态转换错误
    TIMEOUT = 'timeout'                            # 超时错误
    VALIDATION = 'validation'                      # 验证错误
    SYSTEM = 'system'                              # 系统错误


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = 'low'        # 低
    MEDIUM = 'medium'  # 中
    HIGH = 'high'      # 高
    CRITICAL = 'critical'  # 严重


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        """初始化错误处理器"""
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self.error_handlers: Dict[ErrorType, Callable] = {}
        self.recovery_strategies: Dict[ErrorType, Callable] = {}
        self.error_stats: Dict[ErrorType, int] = {error_type: 0 for error_type in ErrorType}
        self.auto_recovery_enabled = True
        
    def handle_error(self, error_type: ErrorType, error_data: Any, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> Dict[str, Any]:
        """
        统一错误处理入口
        
        Args:
            error_type: 错误类型
            error_data: 错误数据
            severity: 错误严重程度
        
        Returns:
            处理结果
        """
        # 记录错误
        error_record = self._record_error(error_type, error_data, severity)
        
        # 更新统计
        self.error_stats[error_type] += 1
        
        # 调用专门处理器
        result = self._handle_specific_error(error_type, error_data, severity)
        
        # 尝试自动恢复
        if self.auto_recovery_enabled:
            recovery_result = self._attempt_recovery(error_type, error_data)
            result['recovery'] = recovery_result
        
        # 记录处理结果
        error_record['handled'] = True
        error_record['result'] = result
        
        logger.error(f"错误已处理: {error_type.value}, 严重程度: {severity.value}")
        return result
    
    def _record_error(self, error_type: ErrorType, error_data: Any, 
                     severity: ErrorSeverity) -> Dict[str, Any]:
        """记录错误"""
        error_record = {
            'id': f"error_{int(time.time() * 1000)}",
            'type': error_type.value,
            'severity': severity.value,
            'data': error_data,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc(),
            'handled': False
        }
        
        self.error_history.append(error_record)
        
        # 限制历史记录大小
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        return error_record
    
    def _handle_specific_error(self, error_type: ErrorType, error_data: Any, 
                              severity: ErrorSeverity) -> Dict[str, Any]:
        """处理特定错误"""
        if error_type in self.error_handlers:
            try:
                return self.error_handlers[error_type](error_data, severity)
            except Exception as e:
                logger.error(f"错误处理器执行失败: {e}")
                return self._get_default_error_response(error_type, error_data)
        else:
            return self._get_default_error_response(error_type, error_data)
    
    def _get_default_error_response(self, error_type: ErrorType, error_data: Any) -> Dict[str, Any]:
        """获取默认错误响应"""
        default_responses = {
            ErrorType.WEBSOCKET_CONNECTION: {
                'success': False,
                'message': 'WebSocket连接错误，请检查网络连接',
                'action': 'reconnect',
                'user_friendly': '网络连接出现问题，正在尝试重新连接...'
            },
            ErrorType.WEBSOCKET_MESSAGE: {
                'success': False,
                'message': 'WebSocket消息处理错误',
                'action': 'retry',
                'user_friendly': '消息发送失败，请重试'
            },
            ErrorType.STATE_TRANSITION: {
                'success': False,
                'message': '状态转换错误',
                'action': 'reset',
                'user_friendly': '系统状态异常，正在重置...'
            },
            ErrorType.TIMEOUT: {
                'success': False,
                'message': '操作超时',
                'action': 'timeout',
                'user_friendly': '操作超时，请稍后重试'
            },
            ErrorType.VALIDATION: {
                'success': False,
                'message': '数据验证错误',
                'action': 'validate',
                'user_friendly': '输入数据有误，请检查后重试'
            },
            ErrorType.SYSTEM: {
                'success': False,
                'message': '系统错误',
                'action': 'restart',
                'user_friendly': '系统出现错误，正在尝试恢复...'
            }
        }
        
        return default_responses.get(error_type, {
            'success': False,
            'message': '未知错误',
            'action': 'unknown',
            'user_friendly': '发生未知错误，请联系技术支持'
        })
    
    def _attempt_recovery(self, error_type: ErrorType, error_data: Any) -> Dict[str, Any]:
        """尝试自动恢复"""
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error_data)
            except Exception as e:
                logger.error(f"恢复策略执行失败: {e}")
                return {'success': False, 'message': f'恢复失败: {e}'}
        else:
            return {'success': False, 'message': '无可用恢复策略'}
    
    def register_error_handler(self, error_type: ErrorType, handler: Callable) -> None:
        """
        注册错误处理器
        
        Args:
            error_type: 错误类型
            handler: 处理器函数
        """
        self.error_handlers[error_type] = handler
        logger.info(f"错误处理器已注册: {error_type.value}")
    
    def unregister_error_handler(self, error_type: ErrorType) -> None:
        """
        注销错误处理器
        
        Args:
            error_type: 错误类型
        """
        if error_type in self.error_handlers:
            del self.error_handlers[error_type]
            logger.info(f"错误处理器已注销: {error_type.value}")
    
    def register_recovery_strategy(self, error_type: ErrorType, strategy: Callable) -> None:
        """
        注册恢复策略
        
        Args:
            error_type: 错误类型
            strategy: 恢复策略函数
        """
        self.recovery_strategies[error_type] = strategy
        logger.info(f"恢复策略已注册: {error_type.value}")
    
    def unregister_recovery_strategy(self, error_type: ErrorType) -> None:
        """
        注销恢复策略
        
        Args:
            error_type: 错误类型
        """
        if error_type in self.recovery_strategies:
            del self.recovery_strategies[error_type]
            logger.info(f"恢复策略已注销: {error_type.value}")
    
    def get_error_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取错误历史
        
        Args:
            limit: 限制返回数量
        
        Returns:
            错误历史列表
        """
        if limit:
            return self.error_history[-limit:]
        return self.error_history.copy()
    
    def clear_error_history(self) -> None:
        """清空错误历史"""
        self.error_history.clear()
        logger.info("错误历史已清空")
    
    def get_error_stats(self) -> Dict[str, int]:
        """
        获取错误统计
        
        Returns:
            错误统计字典
        """
        return {error_type.value: count for error_type, count in self.error_stats.items()}
    
    def reset_error_stats(self) -> None:
        """重置错误统计"""
        self.error_stats = {error_type: 0 for error_type in ErrorType}
        logger.info("错误统计已重置")
    
    def get_errors_by_type(self, error_type: ErrorType) -> List[Dict[str, Any]]:
        """
        获取特定类型的错误
        
        Args:
            error_type: 错误类型
        
        Returns:
            错误列表
        """
        return [
            error for error in self.error_history 
            if error['type'] == error_type.value
        ]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Dict[str, Any]]:
        """
        获取特定严重程度的错误
        
        Args:
            severity: 错误严重程度
        
        Returns:
            错误列表
        """
        return [
            error for error in self.error_history 
            if error['severity'] == severity.value
        ]
    
    def get_recent_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取最近的错误
        
        Args:
            hours: 时间范围（小时）
        
        Returns:
            错误列表
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        return [
            error for error in self.error_history
            if datetime.fromisoformat(error['timestamp']).timestamp() > cutoff_time
        ]
    
    def set_auto_recovery(self, enabled: bool) -> None:
        """
        设置自动恢复
        
        Args:
            enabled: 是否启用自动恢复
        """
        self.auto_recovery_enabled = enabled
        logger.info(f"自动恢复已{'启用' if enabled else '禁用'}")
    
    def get_manager_info(self) -> Dict[str, Any]:
        """
        获取管理器信息
        
        Returns:
            管理器信息字典
        """
        return {
            'history_size': len(self.error_history),
            'max_history_size': self.max_history_size,
            'auto_recovery': self.auto_recovery_enabled,
            'error_stats': self.get_error_stats(),
            'registered_handlers': len(self.error_handlers),
            'recovery_strategies': len(self.recovery_strategies)
        }


# 便捷函数
def create_error_handler() -> ErrorHandler:
    """
    创建错误处理器
    
    Returns:
        错误处理器实例
    """
    return ErrorHandler()


def get_error_type_name(error_type: ErrorType) -> str:
    """
    获取错误类型名称
    
    Args:
        error_type: 错误类型枚举
    
    Returns:
        类型名称
    """
    return error_type.value


def get_error_severity_name(severity: ErrorSeverity) -> str:
    """
    获取错误严重程度名称
    
    Args:
        severity: 错误严重程度枚举
    
    Returns:
        严重程度名称
    """
    return severity.value


def is_valid_error_type(type_name: str) -> bool:
    """
    检查错误类型名称是否有效
    
    Args:
        type_name: 类型名称
    
    Returns:
        是否有效
    """
    try:
        ErrorType(type_name)
        return True
    except ValueError:
        return False


def is_valid_error_severity(severity_name: str) -> bool:
    """
    检查错误严重程度名称是否有效
    
    Args:
        severity_name: 严重程度名称
    
    Returns:
        是否有效
    """
    try:
        ErrorSeverity(severity_name)
        return True
    except ValueError:
        return False
