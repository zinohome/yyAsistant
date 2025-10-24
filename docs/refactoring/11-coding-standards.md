# 代码规范

## 📋 总体规范

### 代码风格
- **Python**：遵循PEP 8标准
- **JavaScript**：遵循ES6+标准
- **HTML/CSS**：遵循W3C标准
- **JSON**：遵循RFC 7159标准

### 命名规范
- **变量名**：小写字母，下划线分隔（snake_case）
- **函数名**：小写字母，下划线分隔（snake_case）
- **类名**：大驼峰命名（PascalCase）
- **常量名**：大写字母，下划线分隔（UPPER_CASE）
- **文件名**：小写字母，下划线分隔（snake_case）

## 🐍 Python代码规范

### 基本规范

#### 1. 导入规范
```python
# 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 第三方库导入
import dash
import pandas as pd

# 本地模块导入
from config.config import config
from core.state_manager import StateManager
```

#### 2. 函数定义规范
```python
def process_message(
    message: str,
    message_type: str = 'text',
    timeout: int = 30
) -> Dict[str, Any]:
    """
    处理消息
    
    Args:
        message: 消息内容
        message_type: 消息类型，默认为'text'
        timeout: 超时时间，默认为30秒
    
    Returns:
        处理结果字典
    
    Raises:
        ValueError: 当消息内容为空时
        TimeoutError: 当处理超时时
    """
    if not message:
        raise ValueError("消息内容不能为空")
    
    # 处理逻辑
    result = {
        'status': 'success',
        'message': message,
        'type': message_type
    }
    
    return result
```

#### 3. 类定义规范
```python
class StateManager:
    """统一状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        self.current_state = State.IDLE
        self.state_history = []
        self.state_locked = False
    
    def set_state(self, new_state: State) -> bool:
        """
        设置状态
        
        Args:
            new_state: 新状态
        
        Returns:
            是否设置成功
        """
        if self.state_locked:
            return False
        
        if self.can_transition(new_state):
            self.state_history.append(self.current_state)
            self.current_state = new_state
            return True
        return False
```

#### 4. 异常处理规范
```python
def handle_websocket_error(error_data: Dict[str, Any]) -> bool:
    """处理WebSocket错误"""
    try:
        # 错误处理逻辑
        if error_data.get('type') == 'connection_failed':
            # 尝试重连
            return self.attempt_reconnect()
        elif error_data.get('type') == 'message_failed':
            # 重试发送消息
            return self.retry_message(error_data.get('message'))
        else:
            # 记录未知错误
            self.log_error(f"未知WebSocket错误: {error_data}")
            return False
    except Exception as e:
        self.log_error(f"处理WebSocket错误时发生异常: {e}")
        return False
```

#### 5. 日志记录规范
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_data(data: str) -> str:
    """处理数据"""
    logger.info(f"开始处理数据: {data[:50]}...")
    
    try:
        # 处理逻辑
        result = perform_processing(data)
        logger.info(f"数据处理完成: {result[:50]}...")
        return result
    except Exception as e:
        logger.error(f"数据处理失败: {e}")
        raise
```

### 代码组织规范

#### 1. 文件结构
```python
# 文件头部注释
"""
模块描述

作者: 开发者姓名
创建时间: 2025-01-15
最后更新: 2025-01-15
版本: 1.0.0
"""

# 导入部分
import os
import sys
from typing import Dict, List, Optional

# 常量定义
DEFAULT_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3

# 类定义
class ExampleClass:
    """示例类"""
    pass

# 函数定义
def example_function():
    """示例函数"""
    pass

# 主程序入口
if __name__ == '__main__':
    main()
```

#### 2. 模块组织
```python
# 模块级文档字符串
"""
状态管理模块

提供统一的状态管理功能，包括状态定义、状态转换、状态锁定等。
"""

# 导入
from typing import Dict, List, Optional
from enum import Enum

# 常量
STATES = {
    'IDLE': 'idle',
    'PROCESSING': 'processing',
    'ERROR': 'error'
}

# 枚举
class State(Enum):
    """状态枚举"""
    IDLE = 'idle'
    PROCESSING = 'processing'
    ERROR = 'error'

# 类定义
class StateManager:
    """状态管理器"""
    pass

# 函数定义
def create_state_manager() -> StateManager:
    """创建状态管理器"""
    return StateManager()
```

## 🟨 JavaScript代码规范

### 基本规范

#### 1. 变量声明
```javascript
// 使用const和let，避免var
const config = new Config();
let currentState = 'idle';

// 对象解构
const { name, version, debug } = config.get('app');

// 数组解构
const [first, second, ...rest] = items;
```

#### 2. 函数定义
```javascript
/**
 * 处理消息
 * @param {string} message - 消息内容
 * @param {string} messageType - 消息类型，默认为'text'
 * @param {number} timeout - 超时时间，默认为30秒
 * @returns {Promise<Object>} 处理结果
 * @throws {Error} 当消息内容为空时
 */
async function processMessage(message, messageType = 'text', timeout = 30) {
    if (!message) {
        throw new Error('消息内容不能为空');
    }
    
    try {
        // 处理逻辑
        const result = await performProcessing(message);
        return {
            status: 'success',
            message: message,
            type: messageType
        };
    } catch (error) {
        console.error('处理消息失败:', error);
        throw error;
    }
}
```

#### 3. 类定义
```javascript
/**
 * 状态管理器
 */
class StateManager {
    /**
     * 构造函数
     */
    constructor() {
        this.currentState = 'idle';
        this.stateHistory = [];
        this.stateLocked = false;
    }
    
    /**
     * 设置状态
     * @param {string} newState - 新状态
     * @returns {boolean} 是否设置成功
     */
    setState(newState) {
        if (this.stateLocked) {
            return false;
        }
        
        if (this.canTransition(newState)) {
            this.stateHistory.push(this.currentState);
            this.currentState = newState;
            return true;
        }
        return false;
    }
    
    /**
     * 检查状态转换是否合法
     * @param {string} newState - 新状态
     * @returns {boolean} 是否合法
     */
    canTransition(newState) {
        const validTransitions = {
            'idle': ['processing', 'error'],
            'processing': ['idle', 'error'],
            'error': ['idle']
        };
        
        return validTransitions[this.currentState]?.includes(newState) || false;
    }
}
```

#### 4. 异步处理
```javascript
/**
 * 处理WebSocket连接
 * @param {string} url - WebSocket URL
 * @returns {Promise<WebSocket>} WebSocket连接
 */
async function connectWebSocket(url) {
    try {
        const ws = new WebSocket(url);
        
        return new Promise((resolve, reject) => {
            ws.onopen = () => {
                console.log('WebSocket连接成功');
                resolve(ws);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket连接失败:', error);
                reject(error);
            };
        });
    } catch (error) {
        console.error('创建WebSocket连接时发生错误:', error);
        throw error;
    }
}
```

#### 5. 错误处理
```javascript
/**
 * 处理WebSocket错误
 * @param {Object} errorData - 错误数据
 * @returns {boolean} 是否处理成功
 */
function handleWebSocketError(errorData) {
    try {
        if (errorData.type === 'connection_failed') {
            // 尝试重连
            return attemptReconnect();
        } else if (errorData.type === 'message_failed') {
            // 重试发送消息
            return retryMessage(errorData.message);
        } else {
            // 记录未知错误
            console.error('未知WebSocket错误:', errorData);
            return false;
        }
    } catch (error) {
        console.error('处理WebSocket错误时发生异常:', error);
        return false;
    }
}
```

### 代码组织规范

#### 1. 文件结构
```javascript
/**
 * 模块描述
 * 
 * 作者: 开发者姓名
 * 创建时间: 2025-01-15
 * 最后更新: 2025-01-15
 * 版本: 1.0.0
 */

// 导入
import { Config } from './config.js';
import { StateManager } from './state-manager.js';

// 常量
const DEFAULT_TIMEOUT = 30;
const MAX_RETRY_ATTEMPTS = 3;

// 类定义
class ExampleClass {
    constructor() {
        // 初始化
    }
}

// 函数定义
function exampleFunction() {
    // 函数体
}

// 主程序入口
if (typeof window !== 'undefined') {
    // 浏览器环境
    window.addEventListener('DOMContentLoaded', () => {
        initialize();
    });
}
```

#### 2. 模块组织
```javascript
/**
 * 状态管理模块
 * 
 * 提供统一的状态管理功能，包括状态定义、状态转换、状态锁定等。
 */

// 导入
import { Config } from './config.js';

// 常量
const STATES = {
    IDLE: 'idle',
    PROCESSING: 'processing',
    ERROR: 'error'
};

// 类定义
class StateManager {
    constructor() {
        this.currentState = STATES.IDLE;
        this.stateHistory = [];
        this.stateLocked = false;
    }
}

// 函数定义
function createStateManager() {
    return new StateManager();
}

// 导出
export { StateManager, STATES, createStateManager };
```

## 📝 文档规范

### 函数文档
```python
def process_message(
    message: str,
    message_type: str = 'text',
    timeout: int = 30
) -> Dict[str, Any]:
    """
    处理消息
    
    Args:
        message: 消息内容
        message_type: 消息类型，默认为'text'
        timeout: 超时时间，默认为30秒
    
    Returns:
        处理结果字典，包含以下字段：
        - status: 处理状态（'success'或'error'）
        - message: 原始消息
        - type: 消息类型
        - result: 处理结果（可选）
    
    Raises:
        ValueError: 当消息内容为空时
        TimeoutError: 当处理超时时
        ConnectionError: 当连接失败时
    
    Example:
        >>> result = process_message("Hello", "text", 30)
        >>> print(result['status'])
        'success'
    """
    pass
```

### 类文档
```python
class StateManager:
    """
    统一状态管理器
    
    提供状态定义、状态转换、状态锁定等功能。
    支持状态历史记录和状态回滚。
    
    Attributes:
        current_state: 当前状态
        state_history: 状态历史记录
        state_locked: 状态是否锁定
    
    Example:
        >>> manager = StateManager()
        >>> manager.set_state(State.PROCESSING)
        >>> print(manager.get_state())
        State.PROCESSING
    """
    
    def __init__(self):
        """初始化状态管理器"""
        pass
```

### 模块文档
```python
"""
状态管理模块

提供统一的状态管理功能，包括：
- 状态定义和枚举
- 状态转换规则
- 状态锁定机制
- 状态历史记录
- 状态回滚功能

主要类：
- State: 状态枚举
- StateManager: 状态管理器
- StateTransition: 状态转换器

主要函数：
- create_state_manager(): 创建状态管理器
- validate_state_transition(): 验证状态转换
- rollback_state(): 回滚状态

使用示例：
    >>> from core.state_manager import StateManager, State
    >>> manager = StateManager()
    >>> manager.set_state(State.PROCESSING)
    >>> print(manager.get_state())
    State.PROCESSING

作者: 开发者姓名
创建时间: 2025-01-15
版本: 1.0.0
"""
```

## 🧪 测试规范

### 单元测试
```python
import unittest
from unittest.mock import Mock, patch
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
        result = self.manager.set_state(State.PROCESSING)
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.PROCESSING)
    
    def test_set_state_invalid_transition(self):
        """测试无效状态转换"""
        result = self.manager.set_state(State.ERROR)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_locking(self):
        """测试状态锁定"""
        self.manager.lock_state()
        result = self.manager.set_state(State.PROCESSING)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_rollback(self):
        """测试状态回滚"""
        self.manager.set_state(State.PROCESSING)
        result = self.manager.rollback_state()
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试
```python
import unittest
from core.state_manager import StateManager
from core.event_manager import EventManager
from core.websocket_manager import WebSocketManager

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.state_manager = StateManager()
        self.event_manager = EventManager()
        self.websocket_manager = WebSocketManager()
    
    def test_state_event_integration(self):
        """测试状态和事件集成"""
        # 注册事件处理器
        self.event_manager.register_handler(
            'TEXT_START',
            lambda data: self.state_manager.set_state(State.TEXT_SSE)
        )
        
        # 触发事件
        self.event_manager.emit_event('TEXT_START', {'message': 'test'})
        
        # 验证状态变化
        self.assertEqual(self.state_manager.get_state(), State.TEXT_SSE)
    
    def test_websocket_state_integration(self):
        """测试WebSocket和状态集成"""
        # 模拟WebSocket连接
        with patch('websockets.connect') as mock_connect:
            mock_ws = Mock()
            mock_connect.return_value = mock_ws
            
            # 连接WebSocket
            result = self.websocket_manager.connect()
            self.assertTrue(result)
            
            # 验证状态
            self.assertEqual(self.state_manager.get_state(), State.IDLE)
```

## 📊 性能规范

### 性能指标
- **响应时间**：< 2秒
- **内存使用**：< 500MB
- **CPU使用**：< 50%
- **错误率**：< 1%

### 性能优化
```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(data):
    """昂贵的计算，使用缓存优化"""
    return perform_calculation(data)

# 使用异步处理
import asyncio

async def process_data_async(data):
    """异步处理数据"""
    tasks = []
    for item in data:
        task = asyncio.create_task(process_item(item))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# 使用生成器
def process_large_dataset(data):
    """处理大数据集，使用生成器"""
    for item in data:
        yield process_item(item)
```

## 🔒 安全规范

### 输入验证
```python
def validate_input(data):
    """验证输入数据"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")
    
    required_fields = ['message', 'type']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
    
    if not isinstance(data['message'], str):
        raise ValueError("消息必须是字符串类型")
    
    if len(data['message']) > 1000:
        raise ValueError("消息长度不能超过1000字符")
```

### 错误处理
```python
def safe_process_data(data):
    """安全处理数据"""
    try:
        # 验证输入
        validate_input(data)
        
        # 处理数据
        result = process_data(data)
        
        # 记录成功
        logger.info(f"数据处理成功: {data['message'][:50]}...")
        
        return result
    except ValueError as e:
        # 记录验证错误
        logger.warning(f"输入验证失败: {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        # 记录系统错误
        logger.error(f"数据处理失败: {e}")
        return {'status': 'error', 'message': '系统错误'}
```

## 📋 代码审查清单

### 代码质量
- [ ] 代码风格符合规范
- [ ] 命名清晰有意义
- [ ] 函数长度适中（< 50行）
- [ ] 类职责单一
- [ ] 注释完整准确

### 功能正确性
- [ ] 功能实现正确
- [ ] 边界条件处理
- [ ] 异常情况处理
- [ ] 输入验证完整
- [ ] 输出格式正确

### 性能优化
- [ ] 算法效率合理
- [ ] 内存使用优化
- [ ] 缓存使用适当
- [ ] 异步处理正确
- [ ] 资源释放及时

### 安全性
- [ ] 输入验证完整
- [ ] 错误信息安全
- [ ] 权限控制正确
- [ ] 数据加密适当
- [ ] 日志记录安全

### 可维护性
- [ ] 代码结构清晰
- [ ] 模块职责明确
- [ ] 依赖关系简单
- [ ] 测试覆盖充分
- [ ] 文档完整准确

---

**总结**：本代码规范涵盖了Python、JavaScript、文档、测试、性能、安全等各个方面，旨在确保代码质量、可维护性和安全性。所有开发人员都应严格遵循这些规范，确保代码的一致性和质量。
