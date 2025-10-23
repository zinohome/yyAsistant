# yyAsistant JavaScript配置系统使用指南

## 🎯 JavaScript配置系统概述

yyAsistant现在使用统一的JavaScript配置系统，解决了所有前端硬编码配置问题，支持动态配置覆盖和本地存储。

## 📁 JavaScript配置文件结构

```
assets/js/
├── app_config.js              # 统一配置类（新增）
├── voice_config.js            # 语音配置（已更新）
├── voice_websocket_manager.js # WebSocket管理器（已更新）
├── realtime_voice_manager.js  # 实时语音管理器（已更新）
├── realtime_adapter_client.js # 适配器客户端（已更新）
├── realtime_api_client.js     # API客户端（已更新）
├── realtime_audio_processor.js # 音频处理器（已更新）
└── realtime_voice_callbacks.js # 语音回调（已更新）
```

## 🔧 配置加载机制

### 1. 配置优先级
1. **用户自定义配置** - localStorage中的用户设置（最高优先级）
2. **服务器配置** - 从服务器API加载的配置（如果可用）
3. **默认配置** - 代码中定义的默认值

### 2. 配置加载顺序
1. `app_config.js` - 统一配置系统（最先加载）
2. `voice_config.js` - 语音配置（兼容性）
3. 其他功能模块配置

## 🚀 使用方法

### 1. 基本使用
```javascript
// 获取配置
console.log(window.appConfig.get('APP_TITLE'));
console.log(window.appConfig.get('WS_URL'));
console.log(window.appConfig.get('YYCHAT_API_KEY'));

// 设置配置
window.appConfig.set('APP_TITLE', '我的应用');
window.appConfig.set('WS_URL', 'ws://localhost:9800/ws/chat');
```

### 2. 便捷方法使用
```javascript
// 获取WebSocket URL
const wsUrl = window.appConfig.getWebSocketUrl();

// 获取后端API URL
const backendUrl = window.appConfig.getBackendUrl();

// 获取API密钥
const apiKey = window.appConfig.getApiKey();

// 获取音频配置
const audioConfig = window.appConfig.getAudioConfig();

// 获取语音配置
const voiceConfig = window.appConfig.getVoiceConfig();

// 检查是否为本地主机
const isLocal = window.appConfig.isLocalhost();
```

### 3. 批量配置
```javascript
// 批量设置配置
window.appConfig.setMultiple({
    'APP_TITLE': '我的应用',
    'WS_URL': 'ws://localhost:9800/ws/chat',
    'YYCHAT_API_KEY': 'my-api-key'
});
```

### 4. 配置验证
```javascript
// 检查配置是否有效
if (window.appConfig.isValid()) {
    console.log('所有配置都有效');
} else {
    console.log('存在无效配置');
}
```

## 📋 主要配置项

### 应用基础配置
- `APP_TITLE` - 应用标题
- `APP_VERSION` - 应用版本

### 服务器配置
- `APP_HOST` - 服务器监听地址
- `APP_PORT` - 服务器端口
- `APP_DEBUG` - 调试模式

### 后端服务配置
- `YYCHAT_HOST` - yychat后端主机
- `YYCHAT_PORT` - yychat后端端口
- `YYCHAT_API_KEY` - yychat API密钥
- `YYCHAT_DEFAULT_MODEL` - 默认模型
- `YYCHAT_DEFAULT_TEMPERATURE` - 默认温度
- `YYCHAT_DEFAULT_STREAM` - 默认流式响应
- `YYCHAT_DEFAULT_USE_TOOLS` - 默认使用工具

### WebSocket配置
- `WS_URL` - WebSocket连接URL
- `WS_RECONNECT_INTERVAL` - 重连间隔
- `WS_MAX_RECONNECT_ATTEMPTS` - 最大重连次数
- `WS_HEARTBEAT_INTERVAL` - 心跳间隔

### 音频配置
- `AUDIO_SAMPLE_RATE` - 音频采样率
- `AUDIO_CHANNELS` - 音频声道数
- `AUDIO_BIT_RATE` - 音频比特率
- `AUDIO_FORMAT` - 音频格式
- `AUDIO_MIME_TYPE` - 音频MIME类型

### 语音配置
- `VOICE_DEFAULT` - 默认语音
- `VOLUME_DEFAULT` - 默认音量
- `AUTO_PLAY_DEFAULT` - 默认自动播放
- `PLAYBACK_VOLUME` - 播放音量
- `PLAYBACK_RATE` - 播放速率

### VAD配置
- `VAD_THRESHOLD` - VAD阈值
- `VAD_SILENCE_DURATION` - 静音持续时间
- `VAD_MAX_SILENCE_DURATION` - 最大静音持续时间
- `VAD_SILENCE_INCREMENT` - 静音增量
- `VAD_NON_ZERO_RATIO_THRESHOLD` - 非零比例阈值

### 录音配置
- `RECORDING_CHUNK_SIZE` - 录音块大小
- `RECORDING_MAX_DURATION` - 最大录音时长
- `AUDIO_CHUNK_SIZE` - 音频块大小
- `AUDIO_SEND_INTERVAL` - 音频发送间隔

### UI配置
- `SHOW_VISUALIZER` - 显示可视化器
- `VISUALIZER_HEIGHT` - 可视化器高度
- `VISUALIZER_WIDTH` - 可视化器宽度

### 调试配置
- `DEBUG_MODE` - 调试模式
- `LOG_LEVEL` - 日志级别

### 测试配置
- `TEST_BASE_URL` - 测试前端URL
- `TEST_BACKEND_URL` - 测试后端URL
- `TEST_LOCALHOST_URL` - 测试本地URL

## 🔄 配置更新流程

### 1. 添加新配置项
1. 在`assets/js/app_config.js`中添加新配置项
2. 添加相应的验证规则
3. 更新相关文档

### 2. 修改现有配置
1. 直接修改`assets/js/app_config.js`中的默认值
2. 测试配置是否正常工作
3. 更新相关文档

## 🧪 测试配置

### 1. 配置加载测试
```javascript
// 在浏览器控制台中测试
console.log('应用标题:', window.appConfig.get('APP_TITLE'));
console.log('WebSocket URL:', window.appConfig.get('WS_URL'));
console.log('API密钥:', window.appConfig.get('YYCHAT_API_KEY'));
```

### 2. 配置覆盖测试
```javascript
// 测试配置覆盖
window.appConfig.set('APP_TITLE', '测试应用');
console.log('应用标题:', window.appConfig.get('APP_TITLE'));

// 测试便捷方法
console.log('WebSocket URL:', window.appConfig.getWebSocketUrl());
console.log('后端URL:', window.appConfig.getBackendUrl());
```

### 3. 配置验证测试
```javascript
// 测试配置验证
console.log('配置是否有效:', window.appConfig.isValid());

// 测试无效配置
window.appConfig.set('APP_PORT', 'invalid');
console.log('配置是否有效:', window.appConfig.isValid());
```

## 🔍 故障排除

### 1. 配置不生效
- 检查`app_config.js`是否正确加载
- 检查配置项名称是否正确
- 检查浏览器控制台是否有错误

### 2. 配置验证失败
- 检查配置值类型是否正确
- 检查数值范围是否在允许范围内
- 检查枚举值是否在允许列表中

### 3. 导入错误
- 确保`app_config.js`在页面中正确加载
- 检查文件路径是否正确
- 检查浏览器是否支持ES6语法

## 🎉 优势总结

- ✅ **零硬编码** - 所有配置都支持动态覆盖
- ✅ **类型安全** - 支持配置验证和类型检查
- ✅ **易维护** - 配置集中管理，易于修改
- ✅ **易测试** - 支持配置验证和测试
- ✅ **向后兼容** - 现有功能完全不受影响
- ✅ **用户友好** - 支持本地存储和用户自定义配置

## 📝 注意事项

1. **加载顺序** - `app_config.js`必须在其他脚本之前加载
2. **兼容性** - 保持与现有`voice_config.js`的兼容性
3. **性能** - 配置加载是异步的，避免阻塞页面渲染
4. **安全性** - 敏感配置（如API密钥）建议通过服务器端配置
