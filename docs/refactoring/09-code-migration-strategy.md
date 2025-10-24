# 代码迁移策略

## 🎯 迁移目标

### 核心目标
1. **保持功能完整性** - 确保所有现有功能正常工作
2. **保持界面稳定性** - 不改变用户界面和交互
3. **提升代码质量** - 重构后的代码更加清晰和可维护
4. **降低技术债务** - 解决现有架构问题

### 迁移原则
- **渐进式迁移**：分阶段、分模块迁移
- **向后兼容**：保持API和接口兼容性
- **充分测试**：每个阶段都要充分测试
- **快速回滚**：出现问题时能够快速回滚

## 📋 迁移策略

### 策略选择：蓝绿部署

#### 蓝绿部署方案
**优势**：
- 风险最小，可以快速回滚
- 不影响现有系统运行
- 可以充分测试新系统
- 用户无感知切换

**劣势**：
- 需要双倍资源
- 部署复杂度较高
- 数据同步需要处理

#### 实施步骤
1. **蓝环境**：当前生产环境
2. **绿环境**：新重构环境
3. **并行运行**：两个环境同时运行
4. **切换验证**：验证新环境功能
5. **流量切换**：将流量切换到新环境
6. **蓝环境下线**：确认新环境稳定后下线旧环境

## 🔄 迁移计划

### 第一阶段：环境准备（1周）

#### 1.1 创建绿环境
```bash
# 创建新的项目目录
mkdir -p /Users/zhangjun/PycharmProjects/yyAsistant-v2
cd /Users/zhangjun/PycharmProjects/yyAsistant-v2

# 复制现有代码
cp -r /Users/zhangjun/PycharmProjects/yyAsistant/* .

# 创建备份目录
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
cp -r * backup/$(date +%Y%m%d_%H%M%S)/
```

#### 1.2 配置新环境
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑.env文件，配置新环境参数

# 初始化数据库
python -m models.init_db
```

#### 1.3 验证环境
```bash
# 运行测试
python -m pytest tests/

# 启动应用
python app.py

# 验证功能
curl http://localhost:8050/health
```

### 第二阶段：核心模块迁移（2-3周）

#### 2.1 状态管理迁移

**迁移步骤**：
1. **创建新状态管理器**
```python
# core/state_manager/state_manager.py
from typing import Dict, List, Optional
from enum import Enum

class State(Enum):
    """状态枚举"""
    IDLE = 'idle'
    TEXT_SSE = 'text_sse'
    TEXT_TTS = 'text_tts'
    VOICE_STT = 'voice_stt'
    VOICE_SSE = 'voice_sse'
    VOICE_TTS = 'voice_tts'
    VOICE_CALL = 'voice_call'
    ERROR = 'error'

class StateManager:
    """统一状态管理器"""
    
    def __init__(self):
        self.current_state = State.IDLE
        self.state_history = []
        self.state_locked = False
        self.state_transitions = {
            State.IDLE: [State.TEXT_SSE, State.VOICE_STT, State.VOICE_CALL],
            State.TEXT_SSE: [State.TEXT_TTS, State.IDLE, State.ERROR],
            State.TEXT_TTS: [State.IDLE, State.ERROR],
            State.VOICE_STT: [State.VOICE_SSE, State.IDLE, State.ERROR],
            State.VOICE_SSE: [State.VOICE_TTS, State.IDLE, State.ERROR],
            State.VOICE_TTS: [State.IDLE, State.ERROR],
            State.VOICE_CALL: [State.IDLE, State.ERROR],
            State.ERROR: [State.IDLE]
        }
    
    def set_state(self, new_state: State) -> bool:
        """设置状态"""
        if self.state_locked:
            return False
        
        if self.can_transition(new_state):
            self.state_history.append(self.current_state)
            self.current_state = new_state
            return True
        return False
    
    def get_state(self) -> State:
        """获取当前状态"""
        return self.current_state
    
    def can_transition(self, new_state: State) -> bool:
        """检查状态转换是否合法"""
        return new_state in self.state_transitions.get(self.current_state, [])
    
    def lock_state(self) -> None:
        """锁定状态"""
        self.state_locked = True
    
    def unlock_state(self) -> None:
        """解锁状态"""
        self.state_locked = False
    
    def rollback_state(self) -> bool:
        """回滚状态"""
        if self.state_history:
            previous_state = self.state_history.pop()
            self.current_state = previous_state
            return True
        return False
```

2. **创建状态管理测试**
```python
# tests/test_state_manager.py
import unittest
from core.state_manager import StateManager, State

class TestStateManager(unittest.TestCase):
    """状态管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = StateManager()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_set_state_success(self):
        """测试设置状态成功"""
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.TEXT_SSE)
    
    def test_set_state_invalid_transition(self):
        """测试无效状态转换"""
        result = self.manager.set_state(State.ERROR)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_locking(self):
        """测试状态锁定"""
        self.manager.lock_state()
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_rollback(self):
        """测试状态回滚"""
        self.manager.set_state(State.TEXT_SSE)
        result = self.manager.rollback_state()
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)

if __name__ == '__main__':
    unittest.main()
```

3. **集成状态管理器**
```python
# app.py
from core.state_manager import StateManager, State

# 创建全局状态管理器
state_manager = StateManager()

# 在回调函数中使用状态管理器
@app.callback(
    Output('ai-chat-x-messages-store', 'data'),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value')
)
def handle_send_message(n_clicks, input_value):
    """处理发送消息"""
    if not n_clicks or not input_value:
        return dash.no_update
    
    # 检查状态
    if not state_manager.can_transition(State.TEXT_SSE):
        return dash.no_update
    
    # 设置状态
    state_manager.set_state(State.TEXT_SSE)
    
    try:
        # 处理消息
        result = process_message(input_value)
        
        # 更新状态
        state_manager.set_state(State.TEXT_TTS)
        
        return result
    except Exception as e:
        # 错误处理
        state_manager.set_state(State.ERROR)
        return {'error': str(e)}
```

#### 2.2 事件管理迁移

**迁移步骤**：
1. **创建事件管理器**
```python
# core/event_manager/event_manager.py
from typing import Dict, List, Callable, Any
from enum import Enum
import asyncio

class Event(Enum):
    """事件枚举"""
    TEXT_START = 'text_start'
    TEXT_SSE_COMPLETE = 'text_sse_complete'
    TEXT_TTS_COMPLETE = 'text_tts_complete'
    VOICE_RECORD_START = 'voice_record_start'
    VOICE_STT_COMPLETE = 'voice_stt_complete'
    VOICE_SSE_COMPLETE = 'voice_sse_complete'
    VOICE_TTS_COMPLETE = 'voice_tts_complete'
    VOICE_CALL_START = 'voice_call_start'
    VOICE_CALL_END = 'voice_call_end'
    ERROR_OCCURRED = 'error_occurred'
    RESET_STATE = 'reset_state'

class EventManager:
    """事件管理器"""
    
    def __init__(self):
        self.event_handlers = {}
        self.event_queue = []
        self.event_processing = False
    
    def register_handler(self, event_type: Event, handler: Callable) -> None:
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: Event, data: Any = None) -> None:
        """触发事件"""
        self.event_queue.append((event_type, data))
        if not self.event_processing:
            asyncio.create_task(self.process_events())
    
    async def process_events(self) -> None:
        """处理事件队列"""
        self.event_processing = True
        while self.event_queue:
            event_type, data = self.event_queue.pop(0)
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        print(f"事件处理错误: {e}")
        self.event_processing = False
```

2. **创建事件处理器**
```python
# core/event_manager/event_handlers.py
from core.state_manager import StateManager, State
from core.event_manager import EventManager, Event

class EventHandlers:
    """事件处理器"""
    
    def __init__(self, state_manager: StateManager, event_manager: EventManager):
        self.state_manager = state_manager
        self.event_manager = event_manager
        self.register_handlers()
    
    def register_handlers(self):
        """注册事件处理器"""
        self.event_manager.register_handler(Event.TEXT_START, self.handle_text_start)
        self.event_manager.register_handler(Event.TEXT_SSE_COMPLETE, self.handle_text_sse_complete)
        self.event_manager.register_handler(Event.TEXT_TTS_COMPLETE, self.handle_text_tts_complete)
        self.event_manager.register_handler(Event.VOICE_RECORD_START, self.handle_voice_record_start)
        self.event_manager.register_handler(Event.VOICE_STT_COMPLETE, self.handle_voice_stt_complete)
        self.event_manager.register_handler(Event.VOICE_SSE_COMPLETE, self.handle_voice_sse_complete)
        self.event_manager.register_handler(Event.VOICE_TTS_COMPLETE, self.handle_voice_tts_complete)
        self.event_manager.register_handler(Event.VOICE_CALL_START, self.handle_voice_call_start)
        self.event_manager.register_handler(Event.VOICE_CALL_END, self.handle_voice_call_end)
        self.event_manager.register_handler(Event.ERROR_OCCURRED, self.handle_error_occurred)
        self.event_manager.register_handler(Event.RESET_STATE, self.handle_reset_state)
    
    def handle_text_start(self, data):
        """处理文本开始事件"""
        self.state_manager.set_state(State.TEXT_SSE)
    
    def handle_text_sse_complete(self, data):
        """处理文本SSE完成事件"""
        self.state_manager.set_state(State.TEXT_TTS)
    
    def handle_text_tts_complete(self, data):
        """处理文本TTS完成事件"""
        self.state_manager.set_state(State.IDLE)
    
    def handle_voice_record_start(self, data):
        """处理语音录音开始事件"""
        self.state_manager.set_state(State.VOICE_STT)
    
    def handle_voice_stt_complete(self, data):
        """处理语音STT完成事件"""
        self.state_manager.set_state(State.VOICE_SSE)
    
    def handle_voice_sse_complete(self, data):
        """处理语音SSE完成事件"""
        self.state_manager.set_state(State.VOICE_TTS)
    
    def handle_voice_tts_complete(self, data):
        """处理语音TTS完成事件"""
        self.state_manager.set_state(State.IDLE)
    
    def handle_voice_call_start(self, data):
        """处理语音通话开始事件"""
        self.state_manager.set_state(State.VOICE_CALL)
    
    def handle_voice_call_end(self, data):
        """处理语音通话结束事件"""
        self.state_manager.set_state(State.IDLE)
    
    def handle_error_occurred(self, data):
        """处理错误发生事件"""
        self.state_manager.set_state(State.ERROR)
    
    def handle_reset_state(self, data):
        """处理重置状态事件"""
        self.state_manager.set_state(State.IDLE)
```

3. **集成事件管理器**
```python
# app.py
from core.event_manager import EventManager, Event
from core.event_manager.event_handlers import EventHandlers

# 创建事件管理器
event_manager = EventManager()

# 创建事件处理器
event_handlers = EventHandlers(state_manager, event_manager)

# 在回调函数中触发事件
@app.callback(
    Output('ai-chat-x-messages-store', 'data'),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value')
)
def handle_send_message(n_clicks, input_value):
    """处理发送消息"""
    if not n_clicks or not input_value:
        return dash.no_update
    
    # 触发事件
    event_manager.emit_event(Event.TEXT_START, {'message': input_value})
    
    try:
        # 处理消息
        result = process_message(input_value)
        
        # 触发事件
        event_manager.emit_event(Event.TEXT_SSE_COMPLETE, {'result': result})
        
        return result
    except Exception as e:
        # 触发错误事件
        event_manager.emit_event(Event.ERROR_OCCURRED, {'error': str(e)})
        return {'error': str(e)}
```

#### 2.3 WebSocket管理迁移

**迁移步骤**：
1. **创建WebSocket管理器**
```python
# core/websocket_manager/websocket_manager.py
import asyncio
import websockets
import json
from typing import Dict, Any, Optional
from config.config import config

class WebSocketManager:
    """WebSocket管理器"""
    
    def __init__(self):
        self.connection = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = config.get('websocket.reconnect_attempts', 5)
        self.reconnect_interval = config.get('websocket.reconnect_interval', 5000)
        self.heartbeat_interval = config.get('websocket.heartbeat_interval', 30000)
        self.heartbeat_task = None
        self.message_handlers = {}
    
    async def connect(self) -> bool:
        """建立连接"""
        try:
            url = config.get('websocket.url')
            self.connection = await websockets.connect(url)
            self.reconnect_attempts = 0
            self.start_heartbeat()
            return True
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            return False
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self.connection:
            await self.connection.close()
            self.connection = None
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """发送消息"""
        if self.connection and not self.connection.closed:
            try:
                await self.connection.send(json.dumps(message))
                return True
            except Exception as e:
                print(f"发送消息失败: {e}")
                return False
        return False
    
    def start_heartbeat(self) -> None:
        """开始心跳检测"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        self.heartbeat_task = asyncio.create_task(self.heartbeat())
    
    async def heartbeat(self) -> None:
        """心跳检测"""
        while True:
            try:
                if self.connection and not self.connection.closed:
                    await self.send_message({
                        'type': 'heartbeat',
                        'timestamp': asyncio.get_event_loop().time()
                    })
                await asyncio.sleep(self.heartbeat_interval / 1000)
            except Exception as e:
                print(f"心跳检测失败: {e}")
                break
    
    async def handle_reconnect(self) -> None:
        """处理重连"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_interval * (2 ** (self.reconnect_attempts - 1))
            await asyncio.sleep(delay / 1000)
            await self.connect()
```

2. **创建WebSocket测试**
```python
# tests/test_websocket_manager.py
import unittest
from unittest.mock import Mock, patch
from core.websocket_manager import WebSocketManager

class TestWebSocketManager(unittest.TestCase):
    """WebSocket管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = WebSocketManager()
    
    @patch('websockets.connect')
    async def test_connect_success(self, mock_connect):
        """测试连接成功"""
        mock_ws = Mock()
        mock_connect.return_value = mock_ws
        
        result = await self.manager.connect()
        self.assertTrue(result)
        self.assertEqual(self.manager.connection, mock_ws)
    
    @patch('websockets.connect')
    async def test_connect_failure(self, mock_connect):
        """测试连接失败"""
        mock_connect.side_effect = Exception("连接失败")
        
        result = await self.manager.connect()
        self.assertFalse(result)
        self.assertIsNone(self.manager.connection)
    
    async def test_send_message_success(self):
        """测试发送消息成功"""
        mock_ws = Mock()
        mock_ws.closed = False
        self.manager.connection = mock_ws
        
        result = await self.manager.send_message({'type': 'test'})
        self.assertTrue(result)
        mock_ws.send.assert_called_once()
    
    async def test_send_message_failure(self):
        """测试发送消息失败"""
        mock_ws = Mock()
        mock_ws.closed = True
        self.manager.connection = mock_ws
        
        result = await self.manager.send_message({'type': 'test'})
        self.assertFalse(result)
```

3. **集成WebSocket管理器**
```python
# app.py
from core.websocket_manager import WebSocketManager

# 创建WebSocket管理器
websocket_manager = WebSocketManager()

# 在应用启动时连接WebSocket
@app.server.before_first_request
def initialize_websocket():
    """初始化WebSocket连接"""
    asyncio.create_task(websocket_manager.connect())

# 在回调函数中使用WebSocket
@app.callback(
    Output('ai-chat-x-messages-store', 'data'),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value')
)
def handle_send_message(n_clicks, input_value):
    """处理发送消息"""
    if not n_clicks or not input_value:
        return dash.no_update
    
    # 发送WebSocket消息
    asyncio.create_task(websocket_manager.send_message({
        'type': 'text_message',
        'content': input_value
    }))
    
    return {'status': 'processing'}
```

### 第三阶段：配置管理迁移（1周）

#### 3.1 创建统一配置

**迁移步骤**：
1. **创建Python配置**
```python
# config/config.py
import os
from typing import Dict, Any

class Config:
    """统一配置管理"""
    
    def __init__(self):
        self.config = {
            # 应用配置
            'app': {
                'name': 'yyAsistant',
                'version': '2.0.0',
                'debug': os.getenv('DEBUG', 'False').lower() == 'true'
            },
            
            # 数据库配置
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite:///yyAsistant.db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20'))
            },
            
            # WebSocket配置
            'websocket': {
                'url': os.getenv('WEBSOCKET_URL', 'ws://localhost:8000/ws'),
                'reconnect_attempts': int(os.getenv('WS_RECONNECT_ATTEMPTS', '5')),
                'reconnect_interval': int(os.getenv('WS_RECONNECT_INTERVAL', '5000')),
                'heartbeat_interval': int(os.getenv('WS_HEARTBEAT_INTERVAL', '30000'))
            },
            
            # 语音配置
            'voice': {
                'synthesis_voice': os.getenv('VOICE_SYNTHESIS_VOICE', 'zh-CN-XiaoxiaoNeural'),
                'synthesis_speed': float(os.getenv('VOICE_SYNTHESIS_SPEED', '1.0')),
                'synthesis_volume': float(os.getenv('VOICE_SYNTHESIS_VOLUME', '1.0')),
                'recognition_language': os.getenv('VOICE_RECOGNITION_LANGUAGE', 'zh-CN')
            },
            
            # 超时配置
            'timeouts': {
                'sse_base': int(os.getenv('SSE_TIMEOUT_BASE', '30')),
                'sse_per_char': float(os.getenv('SSE_TIMEOUT_PER_CHAR', '0.1')),
                'sse_max': int(os.getenv('SSE_TIMEOUT_MAX', '300')),
                'tts_base': int(os.getenv('TTS_TIMEOUT_BASE', '60')),
                'tts_per_char': float(os.getenv('TTS_TIMEOUT_PER_CHAR', '0.2')),
                'tts_max': int(os.getenv('TTS_TIMEOUT_MAX', '600')),
                'stt_base': int(os.getenv('STT_TIMEOUT_BASE', '30')),
                'stt_per_char': float(os.getenv('STT_TIMEOUT_PER_CHAR', '0.05')),
                'stt_max': int(os.getenv('STT_TIMEOUT_MAX', '180'))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

# 全局配置实例
config = Config()
```

2. **创建JavaScript配置**
```javascript
// config/config.js
class Config {
    constructor() {
        this.config = {
            // 应用配置
            app: {
                name: 'yyAsistant',
                version: '2.0.0',
                debug: window.location.hostname === 'localhost'
            },
            
            // WebSocket配置
            websocket: {
                url: this.getWebSocketUrl(),
                reconnectAttempts: 5,
                reconnectInterval: 5000,
                heartbeatInterval: 30000
            },
            
            // 语音配置
            voice: {
                synthesisVoice: 'zh-CN-XiaoxiaoNeural',
                synthesisSpeed: 1.0,
                synthesisVolume: 1.0,
                recognitionLanguage: 'zh-CN'
            },
            
            // 超时配置
            timeouts: {
                sseBase: 30,
                ssePerChar: 0.1,
                sseMax: 300,
                ttsBase: 60,
                ttsPerChar: 0.2,
                ttsMax: 600,
                sttBase: 30,
                sttPerChar: 0.05,
                sttMax: 180
            }
        };
    }
    
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws`;
    }
    
    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        return value;
    }
    
    set(key, value) {
        const keys = key.split('.');
        let config = this.config;
        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in config) || typeof config[k] !== 'object') {
                config[k] = {};
            }
            config = config[k];
        }
        config[keys[keys.length - 1]] = value;
    }
}

// 全局配置实例
window.config = new Config();
```

3. **迁移现有配置**
```bash
# 备份现有配置
cp -r configs/ backup/configs_$(date +%Y%m%d_%H%M%S)/

# 迁移配置到新结构
python scripts/migrate_config.py

# 验证配置
python scripts/validate_config.py
```

### 第四阶段：错误处理迁移（1周）

#### 4.1 创建统一错误处理

**迁移步骤**：
1. **创建错误处理器**
```python
# core/error_handler/error_handler.py
from typing import Dict, Any, Optional
from enum import Enum
import logging

class ErrorType(Enum):
    """错误类型枚举"""
    WEBSOCKET_CONNECTION = 'websocket_connection'
    WEBSOCKET_MESSAGE = 'websocket_message'
    STATE_TRANSITION = 'state_transition'
    TIMEOUT = 'timeout'
    VALIDATION = 'validation'
    SYSTEM = 'system'

class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.error_handlers = {}
        self.error_history = []
        self.logger = logging.getLogger(__name__)
        self.register_handlers()
    
    def register_handlers(self):
        """注册错误处理器"""
        self.error_handlers[ErrorType.WEBSOCKET_CONNECTION] = self.handle_websocket_error
        self.error_handlers[ErrorType.STATE_TRANSITION] = self.handle_state_error
        self.error_handlers[ErrorType.TIMEOUT] = self.handle_timeout_error
        self.error_handlers[ErrorType.VALIDATION] = self.handle_validation_error
        self.error_handlers[ErrorType.SYSTEM] = self.handle_system_error
    
    def handle_error(self, error_type: ErrorType, error_data: Dict[str, Any]) -> bool:
        """处理错误"""
        try:
            if error_type in self.error_handlers:
                result = self.error_handlers[error_type](error_data)
                self.error_history.append({
                    'type': error_type,
                    'data': error_data,
                    'timestamp': time.time(),
                    'handled': result
                })
                return result
            else:
                return self.handle_generic_error(error_data)
        except Exception as e:
            self.logger.error(f"处理错误时发生异常: {e}")
            return False
    
    def handle_websocket_error(self, error_data: Dict[str, Any]) -> bool:
        """处理WebSocket错误"""
        try:
            if error_data.get('type') == 'connection_failed':
                # 尝试重连
                return self.attempt_reconnect()
            elif error_data.get('type') == 'message_failed':
                # 重试发送消息
                return self.retry_message(error_data.get('message'))
            else:
                # 记录未知错误
                self.logger.error(f"未知WebSocket错误: {error_data}")
                return False
        except Exception as e:
            self.logger.error(f"处理WebSocket错误时发生异常: {e}")
            return False
    
    def handle_state_error(self, error_data: Dict[str, Any]) -> bool:
        """处理状态错误"""
        try:
            # 状态回滚逻辑
            return self.rollback_state()
        except Exception as e:
            self.logger.error(f"处理状态错误时发生异常: {e}")
            return False
    
    def handle_timeout_error(self, error_data: Dict[str, Any]) -> bool:
        """处理超时错误"""
        try:
            # 超时处理逻辑
            return self.handle_timeout(error_data)
        except Exception as e:
            self.logger.error(f"处理超时错误时发生异常: {e}")
            return False
    
    def handle_validation_error(self, error_data: Dict[str, Any]) -> bool:
        """处理验证错误"""
        try:
            # 验证错误处理逻辑
            return self.handle_validation(error_data)
        except Exception as e:
            self.logger.error(f"处理验证错误时发生异常: {e}")
            return False
    
    def handle_system_error(self, error_data: Dict[str, Any]) -> bool:
        """处理系统错误"""
        try:
            # 系统错误处理逻辑
            return self.handle_system(error_data)
        except Exception as e:
            self.logger.error(f"处理系统错误时发生异常: {e}")
            return False
    
    def handle_generic_error(self, error_data: Dict[str, Any]) -> bool:
        """处理通用错误"""
        try:
            self.logger.error(f"处理通用错误: {error_data}")
            return False
        except Exception as e:
            self.logger.error(f"处理通用错误时发生异常: {e}")
            return False
```

2. **创建错误处理测试**
```python
# tests/test_error_handler.py
import unittest
from unittest.mock import Mock, patch
from core.error_handler import ErrorHandler, ErrorType

class TestErrorHandler(unittest.TestCase):
    """错误处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.handler = ErrorHandler()
    
    def test_handle_websocket_error(self):
        """测试处理WebSocket错误"""
        error_data = {'type': 'connection_failed'}
        result = self.handler.handle_error(ErrorType.WEBSOCKET_CONNECTION, error_data)
        self.assertIsInstance(result, bool)
    
    def test_handle_state_error(self):
        """测试处理状态错误"""
        error_data = {'from_state': 'idle', 'to_state': 'processing'}
        result = self.handler.handle_error(ErrorType.STATE_TRANSITION, error_data)
        self.assertIsInstance(result, bool)
    
    def test_handle_timeout_error(self):
        """测试处理超时错误"""
        error_data = {'timeout_type': 'sse', 'duration': 30}
        result = self.handler.handle_error(ErrorType.TIMEOUT, error_data)
        self.assertIsInstance(result, bool)
    
    def test_handle_validation_error(self):
        """测试处理验证错误"""
        error_data = {'field': 'message', 'value': '', 'rule': 'required'}
        result = self.handler.handle_error(ErrorType.VALIDATION, error_data)
        self.assertIsInstance(result, bool)
    
    def test_handle_system_error(self):
        """测试处理系统错误"""
        error_data = {'component': 'database', 'operation': 'query'}
        result = self.handler.handle_error(ErrorType.SYSTEM, error_data)
        self.assertIsInstance(result, bool)
```

3. **集成错误处理器**
```python
# app.py
from core.error_handler import ErrorHandler, ErrorType

# 创建错误处理器
error_handler = ErrorHandler()

# 在回调函数中使用错误处理器
@app.callback(
    Output('ai-chat-x-messages-store', 'data'),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value')
)
def handle_send_message(n_clicks, input_value):
    """处理发送消息"""
    if not n_clicks or not input_value:
        return dash.no_update
    
    try:
        # 处理消息
        result = process_message(input_value)
        return result
    except Exception as e:
        # 处理错误
        error_handler.handle_error(ErrorType.SYSTEM, {
            'component': 'message_handler',
            'operation': 'process_message',
            'error': str(e)
        })
        return {'error': str(e)}
```

### 第五阶段：测试和验证（1-2周）

#### 5.1 单元测试

**测试覆盖**：
- 状态管理器测试
- 事件管理器测试
- WebSocket管理器测试
- 配置管理器测试
- 错误处理器测试

**测试执行**：
```bash
# 运行单元测试
python -m pytest tests/unit/ -v

# 生成测试报告
python -m pytest tests/unit/ --html=reports/unit_test_report.html

# 检查测试覆盖率
python -m pytest tests/unit/ --cov=core --cov-report=html
```

#### 5.2 集成测试

**测试覆盖**：
- 状态管理集成测试
- 事件处理集成测试
- WebSocket连接集成测试
- 配置管理集成测试
- 错误处理集成测试

**测试执行**：
```bash
# 运行集成测试
python -m pytest tests/integration/ -v

# 生成集成测试报告
python -m pytest tests/integration/ --html=reports/integration_test_report.html
```

#### 5.3 端到端测试

**测试覆盖**：
- 文本聊天功能测试
- 录音聊天功能测试
- 语音通话功能测试
- 错误处理测试
- 性能测试

**测试执行**：
```bash
# 运行端到端测试
python -m pytest tests/e2e/ -v

# 生成端到端测试报告
python -m pytest tests/e2e/ --html=reports/e2e_test_report.html
```

## 🔄 回滚策略

### 回滚触发条件
- 功能测试失败率 > 5%
- 性能测试不达标
- 用户反馈严重问题
- 系统稳定性问题

### 回滚步骤
1. **停止新环境**
```bash
# 停止新环境服务
pkill -f "python app.py"
```

2. **恢复旧环境**
```bash
# 启动旧环境
cd /Users/zhangjun/PycharmProjects/yyAsistant
python app.py
```

3. **验证恢复**
```bash
# 验证旧环境功能
curl http://localhost:8050/health
```

4. **问题分析**
```bash
# 分析问题原因
python scripts/analyze_issues.py
```

5. **修复问题**
```bash
# 修复发现的问题
python scripts/fix_issues.py
```

## 📊 迁移监控

### 监控指标
- **功能指标**：功能可用性、响应时间、错误率
- **性能指标**：CPU使用率、内存使用率、网络延迟
- **用户指标**：用户满意度、功能使用率、错误反馈

### 监控工具
- **系统监控**：htop、iostat、netstat
- **应用监控**：日志分析、性能分析
- **用户监控**：用户反馈、使用统计

### 监控报告
```bash
# 生成监控报告
python scripts/generate_monitoring_report.py

# 发送监控报告
python scripts/send_monitoring_report.py
```

## 🎯 迁移成功标准

### 功能标准
- [ ] 所有现有功能正常工作
- [ ] 状态管理稳定可靠
- [ ] WebSocket连接稳定
- [ ] 事件处理无冲突
- [ ] 错误处理用户友好

### 性能标准
- [ ] 响应时间 < 2秒
- [ ] 内存使用 < 500MB
- [ ] CPU使用 < 50%
- [ ] 错误率 < 1%

### 质量标准
- [ ] 代码覆盖率 > 80%
- [ ] 单元测试通过率 100%
- [ ] 集成测试通过率 100%
- [ ] 端到端测试通过率 100%

---

**总结**：本迁移策略通过蓝绿部署、渐进式迁移、充分测试、快速回滚等方式，确保迁移过程的安全性和可控性。每个阶段都有明确的目标、任务和验证标准，确保迁移成功。
