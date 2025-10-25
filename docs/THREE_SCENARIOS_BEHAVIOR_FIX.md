# 三个场景行为模式修复报告

## 🎯 用户要求的行为模式

### 场景一：文本聊天
- **音频可视化区域**: 不显示
- **播放指示器**: TTS播放时显示，播放完成后隐藏
- **按钮图标**: 处理中显示旋转图标

### 场景二：录音聊天
- **音频可视化区域**: 仅录音时显示
- **录音波形**: 录音时显示录音波形
- **播放指示器**: TTS播放时显示，播放完成后隐藏
- **按钮图标**: 录音中显示停止图标，处理中显示旋转图标

### 场景三：语音通话
- **音频可视化区域**: 语音通话整个过程中都显示
- **用户语音波形**: 用户说话时显示用户语音波形（类似于录音波形）
- **播放指示器**: 不显示（AI回答时直接播放，不显示播放指示器）
- **按钮图标**: 通话中显示挂断图标
- **点击挂断图标后**: 音频可视化区域隐藏

## 🛠️ 修复内容

### 1. 场景二：录音聊天时显示音频可视化区域

**文件**: `assets/js/voice_recorder_enhanced.js`

**修复内容**:
```javascript
showRecordingWaveform() {
    // 录音聊天：显示音频可视化区域
    const audioVisualizerContainer = document.getElementById('audio-visualizer-container');
    const audioVisualizer = document.getElementById('audio-visualizer');
    
    if (audioVisualizerContainer && audioVisualizer) {
        // 显示音频可视化区域
        audioVisualizerContainer.style.display = 'inline-block';
        console.log('🎨 录音聊天：显示音频可视化区域');
        
        // 初始化增强的音频可视化器
        if (window.enhancedAudioVisualizer) {
            window.enhancedAudioVisualizer.updateState('recording');
            console.log('🎨 录音聊天：更新音频可视化器状态为录音');
        }
        
        // 开始波形动画
        this.startWaveformAnimation(audioVisualizer);
    }
}
```

### 2. 场景三：语音通话时用户说话显示用户语音波形

**文件**: `assets/js/voice_websocket_manager.js`

**已有功能**:
```javascript
// 🎨 更新音频可视化器状态：用户说话时显示录音波形
if (isUserSpeaking && window.enhancedAudioVisualizer) {
    if (this.currentVisualizerState !== 'recording') {
        window.enhancedAudioVisualizer.updateState('recording');
        this.currentVisualizerState = 'recording';
        console.log('🎨 语音通话：用户说话，显示录音波形');
    }
} else if (!isUserSpeaking && window.enhancedAudioVisualizer) {
    if (this.currentVisualizerState !== 'listening') {
        window.enhancedAudioVisualizer.updateState('listening');
        this.currentVisualizerState = 'listening';
        console.log('🎨 语音通话：用户停止说话，显示聆听状态');
    }
}
```

### 3. 场景三：语音通话结束时隐藏音频可视化区域

**文件**: `assets/js/realtime_voice_callbacks.js`

**修复内容**:
```javascript
// 立即隐藏音频可视化区域
if (window.voiceWebSocketManager) {
    window.voiceWebSocketManager.hideAudioVisualizer();
    console.log('🎨 语音通话：点击挂断图标后隐藏音频可视化区域');
}
```

## 🎨 音频可视化区域状态文本功能

### 状态文本显示位置
- **HTML元素**: `realtime-status-text` (id="realtime-status-text")
- **位置**: 音频可视化区域内
- **样式**: 12px字体，颜色根据状态变化

### 状态文本更新逻辑
**文件**: `assets/js/voice_websocket_manager.js`

```javascript
updateStatusIndicator(text, color) {
    const statusElement = document.getElementById('realtime-status-text');
    const canvasElement = document.getElementById('audio-visualizer');
    
    // 更新文本状态指示器
    if (statusElement) {
        statusElement.textContent = text;
        statusElement.style.color = color === 'green' ? '#52c41a' : 
                                  color === 'blue' ? '#1890ff' : 
                                  color === 'orange' ? '#fa8c16' :
                                  color === 'red' ? '#ff4d4f' : 
                                  color === 'gray' ? '#8c8c8c' : '#333333';
    }
    
    // 在音频可视化画布上显示状态文字
    if (canvasElement && window.audioVisualizer) {
        window.audioVisualizer.updateStatusText(text, color);
    }
    
    console.log('🔄 状态指示器已更新:', {text, color});
}
```

### 状态文本颜色方案
- **蓝色(blue)**: 等待/准备状态 (等待用户说话、正在说话、通话中)
- **绿色(green)**: AI回复/成功状态 (AI回复中、已停止回复)
- **橙色(orange)**: 处理中/思考状态 (AI思考中...)
- **红色(red)**: 错误/打断状态 (用户打断)
- **灰色(gray)**: 停止/结束状态 (等待开始、通话已停止)

## 📋 三个场景的完整行为

### 场景一：文本聊天
- **音频可视化区域**: 不显示 ❌
- **播放指示器**: TTS播放时显示，播放完成后隐藏 ✅
- **按钮图标**: 处理中显示旋转图标 ✅
- **状态文本**: 不显示

### 场景二：录音聊天
- **音频可视化区域**: 仅录音时显示 ✅
- **录音波形**: 录音时显示录音波形 ✅
- **播放指示器**: TTS播放时显示，播放完成后隐藏 ✅
- **按钮图标**: 录音中显示停止图标，处理中显示旋转图标 ✅
- **状态文本**: 录音时显示"正在录音"，处理时显示"AI思考中..."

### 场景三：语音通话
- **音频可视化区域**: 语音通话整个过程中都显示 ✅
- **用户语音波形**: 用户说话时显示用户语音波形 ✅
- **播放指示器**: 不显示（AI回答时直接播放） ✅
- **按钮图标**: 通话中显示挂断图标 ✅
- **点击挂断图标后**: 音频可视化区域隐藏 ✅
- **状态文本**: 
  - 通话中显示"通话中，等待用户说话"
  - 用户说话时显示"正在说话"
  - AI思考时显示"AI思考中..."
  - AI回复时显示"AI回复中"

## 🎯 状态文本的具体显示

### 场景二：录音聊天状态文本
- **录音时**: "正在录音" (蓝色)
- **处理中**: "AI思考中..." (橙色)
- **TTS播放时**: "正在播放语音..." (绿色)
- **完成时**: 隐藏状态文本

### 场景三：语音通话状态文本
- **通话开始**: "通话中，等待用户说话" (蓝色)
- **用户说话**: "正在说话" (蓝色)
- **AI思考**: "AI思考中..." (橙色)
- **AI回复**: "AI回复中" (绿色)
- **用户打断**: "用户打断" (红色)
- **通话结束**: 隐藏状态文本

## 📁 修复文件列表

1. **`assets/js/voice_recorder_enhanced.js`** - 修复录音聊天时显示音频可视化区域
2. **`assets/js/realtime_voice_callbacks.js`** - 修复语音通话结束时隐藏音频可视化区域
3. **`docs/THREE_SCENARIOS_BEHAVIOR_FIX.md`** - 新增三个场景行为模式修复报告

## ✅ 修复效果

### 修复前
- 场景二：录音聊天时不显示音频可视化区域
- 场景三：语音通话结束时音频可视化区域不隐藏

### 修复后
- 场景二：录音聊天时正确显示音频可视化区域和状态文本
- 场景三：语音通话时正确显示用户语音波形和状态文本
- 场景三：语音通话结束时正确隐藏音频可视化区域

## 🔄 后续监控

建议在修复后监控以下指标：

1. **场景二录音聊天**: 音频可视化区域是否正确显示
2. **场景二录音聊天**: 状态文本是否正确显示
3. **场景三语音通话**: 用户说话时是否显示用户语音波形
4. **场景三语音通话**: 状态文本是否正确显示
5. **场景三语音通话**: 点击挂断图标后音频可视化区域是否正确隐藏

---

**修复完成时间**: 2024-10-24  
**修复状态**: ✅ 已完成  
**测试状态**: 🧪 待验证
