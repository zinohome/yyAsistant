"""
健康检查模块

提供系统健康检查功能，包括状态检查、性能检查、依赖检查等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, List, Any, Optional, Callable
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheck:
    """健康检查项"""
    
    def __init__(self, name: str, check_func: Callable[[], bool], 
                 timeout: float = 5.0, critical: bool = False):
        """
        初始化健康检查项
        
        Args:
            name: 检查项名称
            check_func: 检查函数
            timeout: 超时时间（秒）
            critical: 是否关键检查项
        """
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.critical = critical
        self.last_check = None
        self.last_result = None
        self.last_error = None
        self.check_count = 0
        self.success_count = 0
    
    def run_check(self) -> bool:
        """
        运行检查
        
        Returns:
            检查是否通过
        """
        try:
            start_time = time.time()
            result = self.check_func()
            duration = time.time() - start_time
            
            self.last_check = datetime.now()
            self.last_result = result
            self.last_error = None
            self.check_count += 1
            
            if result:
                self.success_count += 1
            
            logger.debug(f"健康检查 '{self.name}' 完成: {result}, 耗时: {duration:.3f}s")
            return result
            
        except Exception as e:
            self.last_check = datetime.now()
            self.last_result = False
            self.last_error = str(e)
            self.check_count += 1
            
            logger.error(f"健康检查 '{self.name}' 失败: {e}")
            return False
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.check_count == 0:
            return 0.0
        return self.success_count / self.check_count
    
    def get_status(self) -> HealthStatus:
        """获取健康状态"""
        if self.last_result is None:
            return HealthStatus.UNKNOWN
        
        if self.last_result:
            return HealthStatus.HEALTHY
        elif self.critical:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.WARNING


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, check_interval: float = 30.0):
        """
        初始化健康检查器
        
        Args:
            check_interval: 检查间隔（秒）
        """
        self.check_interval = check_interval
        self.checks = {}
        self.check_thread = None
        self.checking_active = False
        self.lock = threading.Lock()
        
        # 健康状态历史
        self.health_history = []
        self.max_history_size = 1000
        
    def add_check(self, name: str, check_func: Callable[[], bool], 
                  timeout: float = 5.0, critical: bool = False) -> None:
        """
        添加健康检查项
        
        Args:
            name: 检查项名称
            check_func: 检查函数
            timeout: 超时时间（秒）
            critical: 是否关键检查项
        """
        with self.lock:
            self.checks[name] = HealthCheck(name, check_func, timeout, critical)
            logger.info(f"健康检查项已添加: {name}")
    
    def remove_check(self, name: str) -> bool:
        """
        移除健康检查项
        
        Args:
            name: 检查项名称
        
        Returns:
            是否移除成功
        """
        with self.lock:
            if name in self.checks:
                del self.checks[name]
                logger.info(f"健康检查项已移除: {name}")
                return True
            return False
    
    def start_checking(self) -> None:
        """开始健康检查"""
        if self.checking_active:
            return
        
        self.checking_active = True
        self.check_thread = threading.Thread(
            target=self._check_loop,
            daemon=True
        )
        self.check_thread.start()
        logger.info(f"健康检查已启动，间隔: {self.check_interval}秒")
    
    def stop_checking(self) -> None:
        """停止健康检查"""
        self.checking_active = False
        if self.check_thread:
            self.check_thread.join(timeout=1.0)
        logger.info("健康检查已停止")
    
    def _check_loop(self) -> None:
        """检查循环"""
        while self.checking_active:
            try:
                self._run_all_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"健康检查循环出错: {e}")
                time.sleep(self.check_interval)
    
    def _run_all_checks(self) -> None:
        """运行所有检查"""
        with self.lock:
            check_results = {}
            
            for name, check in self.checks.items():
                try:
                    result = check.run_check()
                    check_results[name] = {
                        'status': check.get_status(),
                        'result': result,
                        'error': check.last_error,
                        'success_rate': check.get_success_rate()
                    }
                except Exception as e:
                    logger.error(f"运行健康检查 '{name}' 时出错: {e}")
                    check_results[name] = {
                        'status': HealthStatus.CRITICAL,
                        'result': False,
                        'error': str(e),
                        'success_rate': check.get_success_rate()
                    }
            
            # 记录健康状态历史
            self._record_health_status(check_results)
    
    def _record_health_status(self, check_results: Dict[str, Any]) -> None:
        """记录健康状态"""
        overall_status = self._calculate_overall_status(check_results)
        
        health_record = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status.value,
            'checks': check_results
        }
        
        self.health_history.append(health_record)
        
        # 限制历史记录大小
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
        
        logger.debug(f"健康状态已记录: {overall_status.value}")
    
    def _calculate_overall_status(self, check_results: Dict[str, Any]) -> HealthStatus:
        """计算整体健康状态"""
        if not check_results:
            return HealthStatus.UNKNOWN
        
        critical_failed = any(
            result['status'] == HealthStatus.CRITICAL
            for result in check_results.values()
        )
        
        if critical_failed:
            return HealthStatus.CRITICAL
        
        warning_count = sum(
            1 for result in check_results.values()
            if result['status'] == HealthStatus.WARNING
        )
        
        if warning_count > 0:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def run_check(self, name: str) -> Optional[bool]:
        """
        运行指定检查项
        
        Args:
            name: 检查项名称
        
        Returns:
            检查结果
        """
        with self.lock:
            if name in self.checks:
                return self.checks[name].run_check()
            return None
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查项"""
        with self.lock:
            results = {}
            for name, check in self.checks.items():
                results[name] = {
                    'result': check.run_check(),
                    'status': check.get_status().value,
                    'error': check.last_error,
                    'success_rate': check.get_success_rate()
                }
            return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        with self.lock:
            if not self.health_history:
                return {
                    'overall_status': HealthStatus.UNKNOWN.value,
                    'checks': {},
                    'history_count': 0
                }
            
            latest_record = self.health_history[-1]
            return {
                'overall_status': latest_record['overall_status'],
                'checks': latest_record['checks'],
                'history_count': len(self.health_history),
                'last_check': latest_record['timestamp']
            }
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取健康历史
        
        Args:
            hours: 时间范围（小时）
        
        Returns:
            健康历史记录
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            return [
                record for record in self.health_history
                if datetime.fromisoformat(record['timestamp']) > cutoff_time
            ]
    
    def get_check_stats(self) -> Dict[str, Any]:
        """获取检查统计"""
        with self.lock:
            stats = {}
            for name, check in self.checks.items():
                stats[name] = {
                    'check_count': check.check_count,
                    'success_count': check.success_count,
                    'success_rate': check.get_success_rate(),
                    'last_check': check.last_check.isoformat() if check.last_check else None,
                    'last_result': check.last_result,
                    'last_error': check.last_error,
                    'critical': check.critical
                }
            return stats
    
    def get_overall_health(self) -> HealthStatus:
        """获取整体健康状态"""
        with self.lock:
            if not self.health_history:
                return HealthStatus.UNKNOWN
            
            latest_record = self.health_history[-1]
            return HealthStatus(latest_record['overall_status'])
    
    def is_healthy(self) -> bool:
        """检查是否健康"""
        return self.get_overall_health() == HealthStatus.HEALTHY
    
    def is_critical(self) -> bool:
        """检查是否严重"""
        return self.get_overall_health() == HealthStatus.CRITICAL
    
    def get_failed_checks(self) -> List[str]:
        """获取失败的检查项"""
        with self.lock:
            failed = []
            for name, check in self.checks.items():
                if check.last_result is False:
                    failed.append(name)
            return failed
    
    def get_critical_failed_checks(self) -> List[str]:
        """获取关键失败的检查项"""
        with self.lock:
            critical_failed = []
            for name, check in self.checks.items():
                if check.last_result is False and check.critical:
                    critical_failed.append(name)
            return critical_failed


# 全局健康检查器实例
health_checker = HealthChecker()


# 便捷函数
def add_health_check(name: str, check_func: Callable[[], bool], 
                    timeout: float = 5.0, critical: bool = False) -> None:
    """添加健康检查项"""
    health_checker.add_check(name, check_func, timeout, critical)


def remove_health_check(name: str) -> bool:
    """移除健康检查项"""
    return health_checker.remove_health_check(name)


def start_health_checking(interval: float = 30.0) -> None:
    """开始健康检查"""
    health_checker.check_interval = interval
    health_checker.start_checking()


def stop_health_checking() -> None:
    """停止健康检查"""
    health_checker.stop_checking()


def run_health_check(name: str) -> Optional[bool]:
    """运行指定健康检查"""
    return health_checker.run_check(name)


def run_all_health_checks() -> Dict[str, Any]:
    """运行所有健康检查"""
    return health_checker.run_all_checks()


def get_health_status() -> Dict[str, Any]:
    """获取健康状态"""
    return health_checker.get_health_status()


def get_health_history(hours: int = 24) -> List[Dict[str, Any]]:
    """获取健康历史"""
    return health_checker.get_health_history(hours)


def is_healthy() -> bool:
    """检查是否健康"""
    return health_checker.is_healthy()


def is_critical() -> bool:
    """检查是否严重"""
    return health_checker.is_critical()


def get_failed_checks() -> List[str]:
    """获取失败的检查项"""
    return health_checker.get_failed_checks()


def get_critical_failed_checks() -> List[str]:
    """获取关键失败的检查项"""
    return health_checker.get_critical_failed_checks()
