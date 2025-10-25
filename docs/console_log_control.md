# 控制台日志控制系统

## 概述

为了减少浏览器控制台中的日志输出，我们在 `config.js` 中实现了一个统一的日志控制系统。

## 配置选项

在 `config.js` 中的 `app.show_console_log` 配置项控制所有日志的显示：

```javascript
app: {
    name: 'yyAsistant',
    version: '2.0.0',
    debug: window.location.hostname === 'localhost',
    show_console_log: true  // 控制台日志显示开关
}
```

## 使用方法

### 1. 使用受控日志替代原生console

**❌ 不要使用：**
```javascript
console.log('这是一条日志');
console.warn('这是一条警告');
console.error('这是一条错误');
```

**✅ 推荐使用：**
```javascript
window.controlledLog.log('这是一条日志');
window.controlledLog.warn('这是一条警告');
window.controlledLog.error('这是一条错误');
window.controlledLog.info('这是一条信息');
window.controlledLog.debug('这是一条调试信息');
```

### 2. 动态控制日志显示

```javascript
// 关闭所有日志
window.setConsoleLogEnabled(false);

// 开启所有日志
window.setConsoleLogEnabled(true);

// 检查当前日志状态
const isLogEnabled = window.config.get('app.show_console_log');
```

### 3. 在代码中使用

```javascript
// 安全的日志输出（如果controlledLog未加载，会回退到原生console）
window.controlledLog?.log('安全日志输出');

// 或者检查是否存在
if (window.controlledLog) {
    window.controlledLog.log('受控日志输出');
} else {
    console.log('回退到原生日志');
}
```

## 配置修改

### 方法1：直接修改config.js
```javascript
// 在config.js中修改
app: {
    show_console_log: false  // 关闭日志
}
```

### 方法2：运行时动态修改
```javascript
// 在浏览器控制台中执行
window.setConsoleLogEnabled(false);  // 关闭日志
window.setConsoleLogEnabled(true);   // 开启日志
```

## 注意事项

1. **兼容性**：使用 `window.controlledLog?.log()` 确保在 `controlledLog` 未加载时不会报错
2. **性能**：当 `show_console_log` 为 `false` 时，日志函数会直接返回，不会执行实际的console输出
3. **调试**：在开发环境中，建议保持 `show_console_log: true` 以便调试

## 迁移指南

### 现有代码迁移

1. **查找所有console使用**：
```bash
grep -r "console\." assets/js/
```

2. **批量替换**：
```javascript
// 替换前
console.log('消息');

// 替换后
window.controlledLog?.log('消息');
```

3. **测试验证**：
```javascript
// 测试日志控制
window.setConsoleLogEnabled(false);  // 应该看不到日志
window.setConsoleLogEnabled(true);   // 应该能看到日志
```

## 示例

### 完整的日志控制示例

```javascript
// 初始化时检查配置
document.addEventListener('DOMContentLoaded', function() {
    const logEnabled = window.config.get('app.show_console_log', true);
    window.controlledLog.log('日志系统已初始化，状态:', logEnabled ? '开启' : '关闭');
});

// 在业务逻辑中使用
function processData(data) {
    window.controlledLog.debug('开始处理数据:', data);
    
    try {
        // 处理逻辑
        const result = processLogic(data);
        window.controlledLog.log('数据处理完成:', result);
        return result;
    } catch (error) {
        window.controlledLog.error('数据处理失败:', error);
        throw error;
    }
}
```

这样，你就可以通过简单的配置控制整个应用的日志输出了！
