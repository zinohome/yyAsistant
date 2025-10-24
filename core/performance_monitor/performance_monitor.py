"""
性能监控模块

提供性能监控和指标收集功能，包括响应时间、资源使用、状态转换等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, List, Any, Optional
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_history_size: int = 1000):
        """
        初始化性能监控器
        
        Args:
            max_history_size: 最大历史记录大小
        """
        self.max_history_size = max_history_size
        self.metrics = {
            'response_times': deque(maxlen=max_history_size),
            'state_transitions': deque(maxlen=max_history_size),
            'event_processing': deque(maxlen=max_history_size),
            'websocket_operations': deque(maxlen=max_history_size),
            'timeout_operations': deque(maxlen=max_history_size),
            'error_occurrences': deque(maxlen=max_history_size)
        }
        
        self.counters = defaultdict(int)
        self.timers = {}
        self.system_metrics = {}
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
    def start_monitoring(self, interval: float = 5.0) -> None:
        """
        开始性能监控
        
        Args:
            interval: 监控间隔（秒）
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self, interval: float) -> None:
        """监控循环"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"性能监控循环出错: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            process = psutil.Process()
            
            self.system_metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'process_cpu_percent': process.cpu_percent(),
                'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                'process_threads': process.num_threads(),
                'process_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
            }
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def record_response_time(self, operation: str, duration: float, metadata: Dict[str, Any] = None) -> None:
        """
        记录响应时间
        
        Args:
            operation: 操作名称
            duration: 持续时间（秒）
            metadata: 元数据
        """
        with self.lock:
            self.metrics['response_times'].append({
                'operation': operation,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            })
            self.counters[f'response_time_{operation}'] += 1
    
    def record_state_transition(self, from_state: str, to_state: str, duration: float = None) -> None:
        """
        记录状态转换
        
        Args:
            from_state: 源状态
            to_state: 目标状态
            duration: 转换持续时间
        """
        with self.lock:
            self.metrics['state_transitions'].append({
                'from_state': from_state,
                'to_state': to_state,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            self.counters[f'state_transition_{from_state}_{to_state}'] += 1
    
    def record_event_processing(self, event_type: str, duration: float, success: bool) -> None:
        """
        记录事件处理
        
        Args:
            event_type: 事件类型
            duration: 处理持续时间
            success: 是否成功
        """
        with self.lock:
            self.metrics['event_processing'].append({
                'event_type': event_type,
                'duration': duration,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
            self.counters[f'event_{event_type}_{"success" if success else "failure"}'] += 1
    
    def record_websocket_operation(self, operation: str, duration: float, success: bool) -> None:
        """
        记录WebSocket操作
        
        Args:
            operation: 操作名称
            duration: 持续时间
            success: 是否成功
        """
        with self.lock:
            self.metrics['websocket_operations'].append({
                'operation': operation,
                'duration': duration,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
            self.counters[f'websocket_{operation}_{"success" if success else "failure"}'] += 1
    
    def record_timeout_operation(self, timeout_type: str, duration: float, triggered: bool) -> None:
        """
        记录超时操作
        
        Args:
            timeout_type: 超时类型
            duration: 持续时间
            triggered: 是否触发超时
        """
        with self.lock:
            self.metrics['timeout_operations'].append({
                'timeout_type': timeout_type,
                'duration': duration,
                'triggered': triggered,
                'timestamp': datetime.now().isoformat()
            })
            self.counters[f'timeout_{timeout_type}_{"triggered" if triggered else "normal"}'] += 1
    
    def record_error(self, error_type: str, severity: str, recovery_time: float = None) -> None:
        """
        记录错误
        
        Args:
            error_type: 错误类型
            severity: 严重程度
            recovery_time: 恢复时间
        """
        with self.lock:
            self.metrics['error_occurrences'].append({
                'error_type': error_type,
                'severity': severity,
                'recovery_time': recovery_time,
                'timestamp': datetime.now().isoformat()
            })
            self.counters[f'error_{error_type}_{severity}'] += 1
    
    def start_timer(self, timer_name: str) -> None:
        """
        开始计时器
        
        Args:
            timer_name: 计时器名称
        """
        self.timers[timer_name] = time.time()
    
    def end_timer(self, timer_name: str, operation: str = None) -> float:
        """
        结束计时器
        
        Args:
            timer_name: 计时器名称
            operation: 操作名称
        
        Returns:
            持续时间（秒）
        """
        if timer_name not in self.timers:
            return 0.0
        
        duration = time.time() - self.timers[timer_name]
        del self.timers[timer_name]
        
        if operation:
            self.record_response_time(operation, duration)
        
        return duration
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Args:
            hours: 时间范围（小时）
        
        Returns:
            性能摘要
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            # 过滤最近的数据
            recent_metrics = {}
            for metric_type, data in self.metrics.items():
                recent_data = [
                    item for item in data
                    if datetime.fromisoformat(item['timestamp']) > cutoff_time
                ]
                recent_metrics[metric_type] = recent_data
            
            # 计算统计信息
            summary = {
                'time_range_hours': hours,
                'total_operations': sum(len(data) for data in recent_metrics.values()),
                'system_metrics': self.system_metrics,
                'counters': dict(self.counters),
                'metrics': {}
            }
            
            # 计算响应时间统计
            response_times = [item['duration'] for item in recent_metrics['response_times']]
            if response_times:
                summary['metrics']['response_times'] = {
                    'count': len(response_times),
                    'avg': sum(response_times) / len(response_times),
                    'min': min(response_times),
                    'max': max(response_times)
                }
            
            # 计算状态转换统计
            state_transitions = recent_metrics['state_transitions']
            if state_transitions:
                summary['metrics']['state_transitions'] = {
                    'count': len(state_transitions),
                    'unique_transitions': len(set(
                        f"{item['from_state']}->{item['to_state']}" 
                        for item in state_transitions
                    ))
                }
            
            # 计算事件处理统计
            event_processing = recent_metrics['event_processing']
            if event_processing:
                success_count = sum(1 for item in event_processing if item['success'])
                summary['metrics']['event_processing'] = {
                    'count': len(event_processing),
                    'success_rate': success_count / len(event_processing),
                    'avg_duration': sum(item['duration'] for item in event_processing) / len(event_processing)
                }
            
            # 计算WebSocket操作统计
            websocket_ops = recent_metrics['websocket_operations']
            if websocket_ops:
                success_count = sum(1 for item in websocket_ops if item['success'])
                summary['metrics']['websocket_operations'] = {
                    'count': len(websocket_ops),
                    'success_rate': success_count / len(websocket_ops),
                    'avg_duration': sum(item['duration'] for item in websocket_ops) / len(websocket_ops)
                }
            
            # 计算超时统计
            timeout_ops = recent_metrics['timeout_operations']
            if timeout_ops:
                triggered_count = sum(1 for item in timeout_ops if item['triggered'])
                summary['metrics']['timeout_operations'] = {
                    'count': len(timeout_ops),
                    'triggered_rate': triggered_count / len(timeout_ops),
                    'avg_duration': sum(item['duration'] for item in timeout_ops) / len(timeout_ops)
                }
            
            # 计算错误统计
            errors = recent_metrics['error_occurrences']
            if errors:
                error_types = defaultdict(int)
                severity_counts = defaultdict(int)
                for error in errors:
                    error_types[error['error_type']] += 1
                    severity_counts[error['severity']] += 1
                
                summary['metrics']['errors'] = {
                    'count': len(errors),
                    'error_types': dict(error_types),
                    'severity_counts': dict(severity_counts)
                }
            
            return summary
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return self.system_metrics.copy()
    
    def get_counters(self) -> Dict[str, int]:
        """获取计数器"""
        return dict(self.counters)
    
    def reset_metrics(self) -> None:
        """重置指标"""
        with self.lock:
            for metric_list in self.metrics.values():
                metric_list.clear()
            self.counters.clear()
            self.timers.clear()
        logger.info("性能指标已重置")
    
    def export_metrics(self, filepath: str) -> None:
        """
        导出指标到文件
        
        Args:
            filepath: 文件路径
        """
        import json
        
        with self.lock:
            data = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {k: list(v) for k, v in self.metrics.items()},
                'counters': dict(self.counters),
                'system_metrics': self.system_metrics
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"性能指标已导出到: {filepath}")


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


# 便捷函数
def start_performance_monitoring(interval: float = 5.0) -> None:
    """开始性能监控"""
    performance_monitor.start_monitoring(interval)


def stop_performance_monitoring() -> None:
    """停止性能监控"""
    performance_monitor.stop_monitoring()


def record_response_time(operation: str, duration: float, metadata: Dict[str, Any] = None) -> None:
    """记录响应时间"""
    performance_monitor.record_response_time(operation, duration, metadata)


def record_state_transition(from_state: str, to_state: str, duration: float = None) -> None:
    """记录状态转换"""
    performance_monitor.record_state_transition(from_state, to_state, duration)


def record_event_processing(event_type: str, duration: float, success: bool) -> None:
    """记录事件处理"""
    performance_monitor.record_event_processing(event_type, duration, success)


def record_websocket_operation(operation: str, duration: float, success: bool) -> None:
    """记录WebSocket操作"""
    performance_monitor.record_websocket_operation(operation, duration, success)


def record_timeout_operation(timeout_type: str, duration: float, triggered: bool) -> None:
    """记录超时操作"""
    performance_monitor.record_timeout_operation(timeout_type, duration, triggered)


def record_error(error_type: str, severity: str, recovery_time: float = None) -> None:
    """记录错误"""
    performance_monitor.record_error(error_type, severity, recovery_time)


def start_timer(timer_name: str) -> None:
    """开始计时器"""
    performance_monitor.start_timer(timer_name)


def end_timer(timer_name: str, operation: str = None) -> float:
    """结束计时器"""
    return performance_monitor.end_timer(timer_name, operation)


def get_performance_summary(hours: int = 1) -> Dict[str, Any]:
    """获取性能摘要"""
    return performance_monitor.get_performance_summary(hours)


def get_system_metrics() -> Dict[str, Any]:
    """获取系统指标"""
    return performance_monitor.get_system_metrics()


def reset_metrics() -> None:
    """重置指标"""
    performance_monitor.reset_metrics()


def export_metrics(filepath: str) -> None:
    """导出指标"""
    performance_monitor.export_metrics(filepath)
