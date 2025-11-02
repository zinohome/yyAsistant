# 悬浮面板调试指南

## 问题现象
悬浮面板没有出现

## 调试步骤

### 1. 在浏览器控制台检查元素是否存在

打开浏览器开发者工具（F12），在控制台中执行：

```javascript
// 检查元素是否存在
document.getElementById('voice-call-text-display')

// 如果返回 null，检查父元素
document.getElementById('ai-chat-x-history')

// 检查配置项
window.voiceConfig?.VOICE_CALL_SHOW_TRANSCRIPTION
```

### 2. 手动触发显示（临时测试）

如果元素存在但没有显示，可以手动触发：

```javascript
const panel = document.getElementById('voice-call-text-display');
if (panel) {
    panel.style.display = 'block';
    console.log('面板已手动显示');
} else {
    console.error('面板元素不存在');
}
```

### 3. 检查日志

查看控制台日志中是否有以下信息：
- `🔍 检查悬浮面板显示条件`
- `✅ 悬浮面板已显示`
- `⚠️ 悬浮面板元素不存在，重试`

### 4. 可能的原因

1. **元素未渲染**：元素在 `voice_call_started` 触发时还未渲染完成
   - 已添加重试机制（最多5次，每次间隔200ms）

2. **配置项未加载**：`window.voiceConfig` 未正确初始化
   - 已添加配置项检查和默认显示逻辑

3. **CSS样式问题**：元素被其他样式覆盖
   - 已确保 `zIndex: 100`

4. **元素位置问题**：元素存在但位置不正确
   - 检查 `position: absolute` 和 `top: 60px`

## 已修复的代码

1. ✅ 添加了详细的调试日志
2. ✅ 添加了重试机制（最多5次）
3. ✅ 优化了配置项检查逻辑（默认显示）
4. ✅ 确保 z-index 正确设置

## 如果仍然不显示

请提供以下信息：
1. 控制台中的完整日志（特别是关于悬浮面板的日志）
2. `document.getElementById('voice-call-text-display')` 的结果
3. `window.voiceConfig` 的内容

