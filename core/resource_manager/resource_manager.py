"""
资源管理器

提供资源管理功能，包括内存管理、连接池、缓存管理等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, List, Any, Optional, Callable
import time
import threading
import weakref
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import gc

logger = logging.getLogger(__name__)


class ResourceManager:
    """资源管理器"""
    
    def __init__(self, max_connections: int = 100, max_cache_size: int = 1000):
        """
        初始化资源管理器
        
        Args:
            max_connections: 最大连接数
            max_cache_size: 最大缓存大小
        """
        self.max_connections = max_connections
        self.max_cache_size = max_cache_size
        
        # 连接池
        self.connections = {}
        self.connection_usage = {}
        self.connection_last_used = {}
        
        # 缓存管理
        self.cache = {}
        self.cache_access_count = defaultdict(int)
        self.cache_last_accessed = {}
        self.cache_creation_time = {}
        
        # 内存管理
        self.memory_usage = deque(maxlen=1000)
        self.memory_threshold = 0.8  # 80%内存使用率阈值
        
        # 清理任务
        self.cleanup_tasks = []
        self.cleanup_interval = 300  # 5分钟清理间隔
        self.cleanup_thread = None
        self.cleanup_active = False
        
        # 锁
        self.lock = threading.RLock()
        
    def start_cleanup(self) -> None:
        """开始清理任务"""
        if self.cleanup_active:
            return
        
        self.cleanup_active = True
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self.cleanup_thread.start()
        logger.info("资源清理任务已启动")
    
    def stop_cleanup(self) -> None:
        """停止清理任务"""
        self.cleanup_active = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=1.0)
        logger.info("资源清理任务已停止")
    
    def _cleanup_loop(self) -> None:
        """清理循环"""
        while self.cleanup_active:
            try:
                self._perform_cleanup()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"资源清理循环出错: {e}")
                time.sleep(self.cleanup_interval)
    
    def _perform_cleanup(self) -> None:
        """执行清理"""
        with self.lock:
            # 清理过期连接
            self._cleanup_expired_connections()
            
            # 清理缓存
            self._cleanup_cache()
            
            # 清理内存
            self._cleanup_memory()
            
            # 执行自定义清理任务
            for task in self.cleanup_tasks:
                try:
                    task()
                except Exception as e:
                    logger.error(f"清理任务执行失败: {e}")
    
    def _cleanup_expired_connections(self) -> None:
        """清理过期连接"""
        current_time = time.time()
        expired_connections = []
        
        for conn_id, last_used in self.connection_last_used.items():
            if current_time - last_used > 3600:  # 1小时未使用
                expired_connections.append(conn_id)
        
        for conn_id in expired_connections:
            self.remove_connection(conn_id)
        
        if expired_connections:
            logger.info(f"清理了 {len(expired_connections)} 个过期连接")
    
    def _cleanup_cache(self) -> None:
        """清理缓存"""
        if len(self.cache) <= self.max_cache_size:
            return
        
        # 按访问次数排序，清理最少使用的
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: self.cache_access_count.get(x[0], 0)
        )
        
        items_to_remove = len(self.cache) - self.max_cache_size
        for i in range(items_to_remove):
            key, _ = sorted_items[i]
            del self.cache[key]
            del self.cache_access_count[key]
            del self.cache_last_accessed[key]
            del self.cache_creation_time[key]
        
        if items_to_remove > 0:
            logger.info(f"清理了 {items_to_remove} 个缓存项")
    
    def _cleanup_memory(self) -> None:
        """清理内存"""
        # 记录当前内存使用
        import psutil
        process = psutil.Process()
        memory_percent = process.memory_info().rss / psutil.virtual_memory().total
        
        self.memory_usage.append({
            'timestamp': datetime.now().isoformat(),
            'memory_percent': memory_percent,
            'memory_mb': process.memory_info().rss / 1024 / 1024
        })
        
        # 如果内存使用率过高，强制垃圾回收
        if memory_percent > self.memory_threshold:
            logger.warning(f"内存使用率过高: {memory_percent:.2%}，执行垃圾回收")
            gc.collect()
    
    def add_connection(self, conn_id: str, connection: Any, max_age: int = 3600) -> bool:
        """
        添加连接
        
        Args:
            conn_id: 连接ID
            connection: 连接对象
            max_age: 最大存活时间（秒）
        
        Returns:
            是否添加成功
        """
        with self.lock:
            if len(self.connections) >= self.max_connections:
                logger.warning(f"连接池已满，无法添加连接: {conn_id}")
                return False
            
            self.connections[conn_id] = connection
            self.connection_usage[conn_id] = 0
            self.connection_last_used[conn_id] = time.time()
            
            logger.debug(f"连接已添加: {conn_id}")
            return True
    
    def get_connection(self, conn_id: str) -> Optional[Any]:
        """
        获取连接
        
        Args:
            conn_id: 连接ID
        
        Returns:
            连接对象
        """
        with self.lock:
            if conn_id in self.connections:
                self.connection_usage[conn_id] += 1
                self.connection_last_used[conn_id] = time.time()
                return self.connections[conn_id]
            return None
    
    def remove_connection(self, conn_id: str) -> bool:
        """
        移除连接
        
        Args:
            conn_id: 连接ID
        
        Returns:
            是否移除成功
        """
        with self.lock:
            if conn_id in self.connections:
                del self.connections[conn_id]
                del self.connection_usage[conn_id]
                del self.connection_last_used[conn_id]
                logger.debug(f"连接已移除: {conn_id}")
                return True
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计"""
        with self.lock:
            return {
                'total_connections': len(self.connections),
                'max_connections': self.max_connections,
                'usage_stats': dict(self.connection_usage),
                'last_used': dict(self.connection_last_used)
            }
    
    def cache_set(self, key: str, value: Any, ttl: int = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        with self.lock:
            self.cache[key] = value
            self.cache_access_count[key] = 0
            self.cache_last_accessed[key] = time.time()
            self.cache_creation_time[key] = time.time()
            
            if ttl:
                # 设置过期时间
                self.cache_creation_time[key] = time.time() + ttl
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值
        """
        with self.lock:
            if key in self.cache:
                # 检查是否过期
                if key in self.cache_creation_time:
                    if time.time() > self.cache_creation_time[key]:
                        del self.cache[key]
                        del self.cache_access_count[key]
                        del self.cache_last_accessed[key]
                        del self.cache_creation_time[key]
                        return None
                
                self.cache_access_count[key] += 1
                self.cache_last_accessed[key] = time.time()
                return self.cache[key]
            return None
    
    def cache_remove(self, key: str) -> bool:
        """
        移除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否移除成功
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.cache_access_count[key]
                del self.cache_last_accessed[key]
                if key in self.cache_creation_time:
                    del self.cache_creation_time[key]
                return True
            return False
    
    def cache_clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.cache_access_count.clear()
            self.cache_last_accessed.clear()
            self.cache_creation_time.clear()
            logger.info("缓存已清空")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            return {
                'total_items': len(self.cache),
                'max_size': self.max_cache_size,
                'access_counts': dict(self.cache_access_count),
                'last_accessed': dict(self.cache_last_accessed)
            }
    
    def add_cleanup_task(self, task: Callable[[], None]) -> None:
        """
        添加清理任务
        
        Args:
            task: 清理任务函数
        """
        self.cleanup_tasks.append(task)
        logger.debug("清理任务已添加")
    
    def remove_cleanup_task(self, task: Callable[[], None]) -> None:
        """
        移除清理任务
        
        Args:
            task: 清理任务函数
        """
        if task in self.cleanup_tasks:
            self.cleanup_tasks.remove(task)
            logger.debug("清理任务已移除")
    
    def get_memory_usage(self) -> List[Dict[str, Any]]:
        """获取内存使用历史"""
        return list(self.memory_usage)
    
    def set_memory_threshold(self, threshold: float) -> None:
        """
        设置内存阈值
        
        Args:
            threshold: 内存使用率阈值（0-1）
        """
        if 0 <= threshold <= 1:
            self.memory_threshold = threshold
            logger.info(f"内存阈值已设置为: {threshold:.2%}")
        else:
            logger.error(f"无效的内存阈值: {threshold}")
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """获取资源摘要"""
        with self.lock:
            return {
                'connections': self.get_connection_stats(),
                'cache': self.get_cache_stats(),
                'memory': {
                    'usage_history': len(self.memory_usage),
                    'threshold': self.memory_threshold,
                    'current_usage': self.memory_usage[-1] if self.memory_usage else None
                },
                'cleanup': {
                    'active': self.cleanup_active,
                    'interval': self.cleanup_interval,
                    'tasks_count': len(self.cleanup_tasks)
                }
            }
    
    def cleanup_all(self) -> None:
        """清理所有资源"""
        with self.lock:
            # 清理连接
            self.connections.clear()
            self.connection_usage.clear()
            self.connection_last_used.clear()
            
            # 清理缓存
            self.cache.clear()
            self.cache_access_count.clear()
            self.cache_last_accessed.clear()
            self.cache_creation_time.clear()
            
            # 清理内存历史
            self.memory_usage.clear()
            
            # 强制垃圾回收
            gc.collect()
            
            logger.info("所有资源已清理")


# 全局资源管理器实例
resource_manager = ResourceManager()


# 便捷函数
def start_resource_cleanup() -> None:
    """开始资源清理"""
    resource_manager.start_cleanup()


def stop_resource_cleanup() -> None:
    """停止资源清理"""
    resource_manager.stop_cleanup()


def add_connection(conn_id: str, connection: Any, max_age: int = 3600) -> bool:
    """添加连接"""
    return resource_manager.add_connection(conn_id, connection, max_age)


def get_connection(conn_id: str) -> Optional[Any]:
    """获取连接"""
    return resource_manager.get_connection(conn_id)


def remove_connection(conn_id: str) -> bool:
    """移除连接"""
    return resource_manager.remove_connection(conn_id)


def cache_set(key: str, value: Any, ttl: int = None) -> None:
    """设置缓存"""
    resource_manager.cache_set(key, value, ttl)


def cache_get(key: str) -> Optional[Any]:
    """获取缓存"""
    return resource_manager.cache_get(key)


def cache_remove(key: str) -> bool:
    """移除缓存"""
    return resource_manager.cache_remove(key)


def cache_clear() -> None:
    """清空缓存"""
    resource_manager.cache_clear()


def add_cleanup_task(task: Callable[[], None]) -> None:
    """添加清理任务"""
    resource_manager.add_cleanup_task(task)


def get_resource_summary() -> Dict[str, Any]:
    """获取资源摘要"""
    return resource_manager.get_resource_summary()


def cleanup_all() -> None:
    """清理所有资源"""
    resource_manager.cleanup_all()
