"""
WebSocket管理模块

提供统一的WebSocket连接管理功能，包括连接、断开、重连、心跳检测等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import asyncio
import websockets
import json
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import threading
from config.config import get_config

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态枚举"""
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    RECONNECTING = 'reconnecting'
    ERROR = 'error'


class WebSocketManager:
    """WebSocket管理器"""
    
    def __init__(self):
        """初始化WebSocket管理器"""
        self.websocket = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.url = get_config('websocket.url')
        self.reconnect_attempts = get_config('websocket.reconnect_attempts', 5)
        self.reconnect_interval = get_config('websocket.reconnect_interval', 5000)
        self.heartbeat_interval = get_config('websocket.heartbeat_interval', 30000)
        
        self.current_attempts = 0
        self.heartbeat_task = None
        self.reconnect_task = None
        self.message_handlers: List[Callable] = []
        self.connection_handlers: List[Callable] = []
        self.error_handlers: List[Callable] = []
        
        self.last_heartbeat = None
        self.heartbeat_timeout = 10  # 心跳超时时间（秒）
        self.max_reconnect_delay = 30000  # 最大重连延迟（毫秒）
        
        self.message_queue: List[Dict] = []
        self.max_queue_size = 100
        
    async def connect(self) -> bool:
        """
        建立WebSocket连接
        
        Returns:
            是否连接成功
        """
        if self.connection_state == ConnectionState.CONNECTED:
            logger.info("WebSocket已连接")
            return True
        
        if self.connection_state == ConnectionState.CONNECTING:
            logger.warning("WebSocket正在连接中")
            return False
        
        try:
            self.connection_state = ConnectionState.CONNECTING
            logger.info(f"正在连接WebSocket: {self.url}")
            
            # 建立连接
            self.websocket = await websockets.connect(
                self.url,
                ping_interval=None,  # 禁用自动ping
                ping_timeout=None,
                close_timeout=10
            )
            
            self.connection_state = ConnectionState.CONNECTED
            self.current_attempts = 0
            
            # 启动心跳检测
            self.start_heartbeat()
            
            # 启动消息监听
            asyncio.create_task(self._message_listener())
            
            # 发送队列中的消息
            await self._send_queued_messages()
            
            # 通知连接处理器
            self._notify_connection_handlers(True)
            
            logger.info("WebSocket连接成功")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self.connection_state = ConnectionState.ERROR
            self._notify_error_handlers(f"连接失败: {e}")
            return False
    
    async def disconnect(self) -> None:
        """断开WebSocket连接"""
        if self.connection_state == ConnectionState.DISCONNECTED:
            return
        
        logger.info("正在断开WebSocket连接")
        
        # 停止心跳检测
        self.stop_heartbeat()
        
        # 停止重连任务
        if self.reconnect_task:
            self.reconnect_task.cancel()
            self.reconnect_task = None
        
        # 关闭连接
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"关闭WebSocket连接时出错: {e}")
            finally:
                self.websocket = None
        
        self.connection_state = ConnectionState.DISCONNECTED
        
        # 通知连接处理器
        self._notify_connection_handlers(False)
        
        logger.info("WebSocket连接已断开")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        发送消息
        
        Args:
            message: 消息字典
        
        Returns:
            是否发送成功
        """
        if self.connection_state != ConnectionState.CONNECTED:
            logger.warning("WebSocket未连接，消息已加入队列")
            self._queue_message(message)
            return False
        
        try:
            message_str = json.dumps(message, ensure_ascii=False)
            await self.websocket.send(message_str)
            logger.debug(f"消息已发送: {message.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self._notify_error_handlers(f"发送消息失败: {e}")
            return False
    
    def _queue_message(self, message: Dict[str, Any]) -> None:
        """将消息加入队列"""
        if len(self.message_queue) >= self.max_queue_size:
            logger.warning("消息队列已满，丢弃最旧的消息")
            self.message_queue.pop(0)
        
        self.message_queue.append({
            'message': message,
            'timestamp': time.time()
        })
    
    async def _send_queued_messages(self) -> None:
        """发送队列中的消息"""
        if not self.message_queue:
            return
        
        logger.info(f"发送队列中的 {len(self.message_queue)} 条消息")
        
        for item in self.message_queue[:]:
            try:
                await self.send_message(item['message'])
                self.message_queue.remove(item)
            except Exception as e:
                logger.error(f"发送队列消息失败: {e}")
                break
    
    async def _message_listener(self) -> None:
        """消息监听器"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self._notify_message_handlers(data)
                except json.JSONDecodeError as e:
                    logger.error(f"解析消息失败: {e}")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket连接已关闭")
            await self._handle_disconnection()
        except Exception as e:
            logger.error(f"消息监听器出错: {e}")
            await self._handle_disconnection()
    
    async def _handle_disconnection(self) -> None:
        """处理连接断开"""
        if self.connection_state == ConnectionState.DISCONNECTED:
            return
        
        logger.warning("WebSocket连接断开")
        self.connection_state = ConnectionState.DISCONNECTED
        self.websocket = None
        
        # 停止心跳检测
        self.stop_heartbeat()
        
        # 通知连接处理器
        self._notify_connection_handlers(False)
        
        # 启动重连
        if self.current_attempts < self.reconnect_attempts:
            await self._schedule_reconnect()
    
    async def _schedule_reconnect(self) -> None:
        """安排重连"""
        if self.reconnect_task:
            return
        
        self.connection_state = ConnectionState.RECONNECTING
        self.current_attempts += 1
        
        # 计算重连延迟（指数退避）
        delay = min(
            self.reconnect_interval * (2 ** (self.current_attempts - 1)),
            self.max_reconnect_delay
        )
        
        logger.info(f"将在 {delay}ms 后尝试重连 (第 {self.current_attempts}/{self.reconnect_attempts} 次)")
        
        self.reconnect_task = asyncio.create_task(self._reconnect_after_delay(delay))
    
    async def _reconnect_after_delay(self, delay: int) -> None:
        """延迟后重连"""
        await asyncio.sleep(delay / 1000)
        
        try:
            logger.info("开始自动重连...")
            success = await self.connect()
            
            if success:
                logger.info("自动重连成功")
            else:
                logger.error("自动重连失败")
                
        except Exception as e:
            logger.error(f"自动重连过程中出错: {e}")
        finally:
            self.reconnect_task = None
    
    def start_heartbeat(self) -> None:
        """开始心跳检测"""
        if self.heartbeat_task:
            return
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("心跳检测已启动")
    
    def stop_heartbeat(self) -> None:
        """停止心跳检测"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
            logger.info("心跳检测已停止")
    
    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        while self.connection_state == ConnectionState.CONNECTED:
            try:
                # 发送心跳
                await self.send_message({
                    'type': 'heartbeat',
                    'timestamp': time.time()
                })
                
                self.last_heartbeat = time.time()
                logger.debug("心跳已发送")
                
                # 等待下次心跳
                await asyncio.sleep(self.heartbeat_interval / 1000)
                
            except Exception as e:
                logger.error(f"心跳检测出错: {e}")
                break
    
    def register_message_handler(self, handler: Callable) -> None:
        """注册消息处理器"""
        self.message_handlers.append(handler)
        logger.info("消息处理器已注册")
    
    def unregister_message_handler(self, handler: Callable) -> None:
        """注销消息处理器"""
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
            logger.info("消息处理器已注销")
    
    def register_connection_handler(self, handler: Callable) -> None:
        """注册连接状态处理器"""
        self.connection_handlers.append(handler)
        logger.info("连接状态处理器已注册")
    
    def unregister_connection_handler(self, handler: Callable) -> None:
        """注销连接状态处理器"""
        if handler in self.connection_handlers:
            self.connection_handlers.remove(handler)
            logger.info("连接状态处理器已注销")
    
    def register_error_handler(self, handler: Callable) -> None:
        """注册错误处理器"""
        self.error_handlers.append(handler)
        logger.info("错误处理器已注册")
    
    def unregister_error_handler(self, handler: Callable) -> None:
        """注销错误处理器"""
        if handler in self.error_handlers:
            self.error_handlers.remove(handler)
            logger.info("错误处理器已注销")
    
    def _notify_message_handlers(self, data: Dict[str, Any]) -> None:
        """通知消息处理器"""
        for handler in self.message_handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"消息处理器执行失败: {e}")
    
    def _notify_connection_handlers(self, connected: bool) -> None:
        """通知连接状态处理器"""
        for handler in self.connection_handlers:
            try:
                handler(connected)
            except Exception as e:
                logger.error(f"连接状态处理器执行失败: {e}")
    
    def _notify_error_handlers(self, error: str) -> None:
        """通知错误处理器"""
        for handler in self.error_handlers:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"错误处理器执行失败: {e}")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connection_state == ConnectionState.CONNECTED
    
    def get_connection_state(self) -> ConnectionState:
        """获取连接状态"""
        return self.connection_state
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            'state': self.connection_state.value,
            'url': self.url,
            'attempts': self.current_attempts,
            'max_attempts': self.reconnect_attempts,
            'queue_size': len(self.message_queue),
            'last_heartbeat': self.last_heartbeat,
            'handlers': {
                'message': len(self.message_handlers),
                'connection': len(self.connection_handlers),
                'error': len(self.error_handlers)
            }
        }
    
    async def force_reconnect(self) -> bool:
        """强制重连"""
        logger.info("强制重连WebSocket")
        
        # 断开当前连接
        await self.disconnect()
        
        # 重置重连计数
        self.current_attempts = 0
        
        # 重新连接
        return await self.connect()


# 便捷函数
def create_websocket_manager() -> WebSocketManager:
    """
    创建WebSocket管理器
    
    Returns:
        WebSocket管理器实例
    """
    return WebSocketManager()


def get_connection_state_name(state: ConnectionState) -> str:
    """
    获取连接状态名称
    
    Args:
        state: 连接状态枚举
    
    Returns:
        状态名称
    """
    return state.value


def is_valid_connection_state(state_name: str) -> bool:
    """
    检查连接状态名称是否有效
    
    Args:
        state_name: 状态名称
    
    Returns:
        是否有效
    """
    try:
        ConnectionState(state_name)
        return True
    except ValueError:
        return False
