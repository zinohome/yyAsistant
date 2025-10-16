# 统一按钮状态管理 - 开发TODO列表

## 项目概述

**目标**: 实现文本按钮、录音按钮、通话按钮的统一状态管理
**预计工期**: 2-3天
**优先级**: P0 (高优先级)

---

## Phase 1: 基础架构搭建 (预计4小时)

### 1.1 创建统一状态管理器 ⏰ 2小时
- [ ] 创建文件 `assets/js/unified_button_state_manager.js`
- [ ] 定义 `UnifiedButtonStateManager` 类
- [ ] 定义全局状态枚举 `GLOBAL_STATES`
- [ ] 实现构造函数和初始化方法
- [ ] 实现状态处理器映射 `initStateHandlers()`

**验收标准**:
- ✅ 文件创建成功
- ✅ 类结构完整
- ✅ 7个全局状态正确定义
- ✅ 控制台输出初始化成功日志

**关键代码**:
```javascript
class UnifiedButtonStateManager {
    constructor() {
        this.GLOBAL_STATES = {
            IDLE: 'idle',
            TEXT_PROCESSING: 'text_processing',
            RECORDING: 'recording',
            VOICE_PROCESSING: 'voice_processing',
            PREPARING_TTS: 'preparing_tts',
            PLAYING_TTS: 'playing_tts',
            CALLING: 'calling'
        };
        this.currentState = this.GLOBAL_STATES.IDLE;
        this.stateHandlers = new Map();
        this.initStateHandlers();
    }
}
```

---

### 1.2 实现按钮更新方法 ⏰ 1小时
- [ ] 实现 `updateTextButton(label, disabled, loading)`
- [ ] 实现 `updateRecordButton(label, icon, color, clickable)`
- [ ] 实现 `updateCallButton(label, icon, color, clickable)`
- [ ] 添加详细的日志输出

**验收标准**:
- ✅ 三个方法正确更新对应按钮
- ✅ Dash属性正确设置
- ✅ 日志输出清晰可读

**测试方法**:
```javascript
// 在浏览器控制台测试
window.unifiedButtonStateManager.updateTextButton('测试', true, true);
window.unifiedButtonStateManager.updateRecordButton('录音', '🎤', '#ff4d4f', true);
window.unifiedButtonStateManager.updateCallButton('通话', '📞', '#52c41a', true);
```

---

### 1.3 实现状态切换方法 ⏰ 1小时
- [ ] 实现 `setState(newState)` 核心方法
- [ ] 实现场景转换方法：
  - [ ] `startTextProcessing()`
  - [ ] `startRecording()`
  - [ ] `stopRecording()`
  - [ ] `sttCompleted()`
  - [ ] `prepareForTTS()`
  - [ ] `startPlayingTTS()`
  - [ ] `stopPlayingOrComplete()`
  - [ ] `resetToIdle()`

**验收标准**:
- ✅ 状态切换日志清晰
- ✅ 状态处理器正确执行
- ✅ 按钮状态正确更新

**测试方法**:
```javascript
// 测试状态切换
window.unifiedButtonStateManager.startTextProcessing();
// 观察按钮变化
window.unifiedButtonStateManager.resetToIdle();
// 观察按钮恢复
```

---

## Phase 2: 输入验证功能 (预计2小时)

### 2.1 实现输入框内容检查 ⏰ 0.5小时
- [ ] 实现 `checkInputContent()` 方法
- [ ] 检查输入框元素是否存在
- [ ] 检查输入框内容是否为空
- [ ] 添加详细的日志输出

**验收标准**:
- ✅ 输入框为空时返回 false
- ✅ 输入框有内容时返回 true
- ✅ 输入框不存在时返回 false 并警告

**测试方法**:
```javascript
// 清空输入框
document.getElementById('ai-chat-x-input').value = '';
console.log(window.unifiedButtonStateManager.checkInputContent()); // false

// 输入内容
document.getElementById('ai-chat-x-input').value = '测试消息';
console.log(window.unifiedButtonStateManager.checkInputContent()); // true
```

---

### 2.2 实现空输入警告提示 ⏰ 0.5小时
- [ ] 实现 `showInputEmptyWarning()` 方法
- [ ] 使用 Ant Design Message 组件显示提示
- [ ] 使用 Dash clientside 更新 global-message

**验收标准**:
- ✅ 输入框为空提交时显示警告
- ✅ 警告提示友好易懂
- ✅ 提示自动消失

**测试方法**:
```javascript
window.unifiedButtonStateManager.showInputEmptyWarning();
// 应该看到警告提示
```

---

### 2.3 实现文本按钮点击处理 ⏰ 1小时
- [ ] 实现 `handleTextButtonClick()` 方法
- [ ] 检查当前状态是否允许提交
- [ ] 检查输入框内容
- [ ] 调用状态切换方法
- [ ] 返回处理结果

**验收标准**:
- ✅ 空闲状态且输入框有内容时返回 true
- ✅ 输入框为空时返回 false 并显示警告
- ✅ 非空闲状态时返回 false

**测试方法**:
```javascript
// 测试空输入
document.getElementById('ai-chat-x-input').value = '';
console.log(window.unifiedButtonStateManager.handleTextButtonClick()); // false

// 测试有内容
document.getElementById('ai-chat-x-input').value = '测试';
console.log(window.unifiedButtonStateManager.handleTextButtonClick()); // true
```

---

## Phase 3: 按钮点击处理 (预计2小时)

### 3.1 实现录音按钮点击处理 ⏰ 1小时
- [ ] 实现 `handleRecordButtonClick()` 方法
- [ ] 处理空闲状态：开始录音
- [ ] 处理录音状态：停止录音
- [ ] 处理播放状态：停止播放
- [ ] 其他状态拒绝操作

**验收标准**:
- ✅ 空闲状态点击开始录音
- ✅ 录音状态点击停止录音
- ✅ 播放状态点击停止播放
- ✅ 其他状态拒绝操作

**测试方法**:
```javascript
// 测试开始录音
window.unifiedButtonStateManager.handleRecordButtonClick();
// 应该看到状态变为 recording

// 测试停止录音
window.unifiedButtonStateManager.handleRecordButtonClick();
// 应该看到状态变为 voice_processing
```

---

### 3.2 实现通话按钮点击处理 ⏰ 1小时
- [ ] 实现 `handleCallButtonClick()` 方法
- [ ] 处理空闲状态：开始通话
- [ ] 处理通话状态：停止通话
- [ ] 其他状态拒绝操作
- [ ] 添加未来实现的占位符

**验收标准**:
- ✅ 空闲状态点击开始通话
- ✅ 通话状态点击停止通话
- ✅ 其他状态拒绝操作
- ✅ 显示未来实现提示

**测试方法**:
```javascript
// 测试开始通话
window.unifiedButtonStateManager.handleCallButtonClick();
// 应该看到状态变为 calling

// 测试停止通话
window.unifiedButtonStateManager.handleCallButtonClick();
// 应该看到状态变为 idle
```

---

## Phase 4: 前端集成 (预计3小时)

### 4.1 在app.py中引入脚本 ⏰ 0.5小时
- [ ] 修改 `app.py` 的 `index_string`
- [ ] 在 `<footer>` 中添加脚本标签
- [ ] 确保脚本加载顺序正确
- [ ] 测试脚本加载成功

**验收标准**:
- ✅ 页面加载时脚本正确引入
- ✅ 控制台显示初始化日志
- ✅ 全局对象 `window.unifiedButtonStateManager` 可用

**关键代码**:
```python
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            <script src="/assets/js/unified_button_state_manager.js"></script>
            <script src="/assets/js/voice_state_manager.js"></script>
            <script src="/assets/js/voice_recorder_enhanced.js"></script>
            <script src="/assets/js/voice_player_enhanced.js"></script>
            {%renderer%}
        </footer>
    </body>
</html>
'''
```

---

### 4.2 录音器集成 ⏰ 1小时
- [ ] 修改 `voice_recorder_enhanced.js`
- [ ] 在 `startRecording()` 中调用状态管理器
- [ ] 在 `stopRecording()` 中调用状态管理器
- [ ] 在 STT 完成时通知状态管理器
- [ ] 移除旧的状态管理逻辑

**验收标准**:
- ✅ 录音开始时按钮变红色
- ✅ 录音停止时按钮变黄色
- ✅ STT完成时文本按钮变busy

**修改位置**:
- `startRecording()` 开始处
- `stopRecording()` 开始处
- `handleTranscriptionResult()` 完成处

---

### 4.3 播放器集成 ⏰ 1小时
- [ ] 修改 `voice_player_enhanced.js`
- [ ] 在播放开始时调用状态管理器
- [ ] 在播放结束时调用状态管理器
- [ ] 在播放错误时重置状态
- [ ] 移除旧的状态管理逻辑

**验收标准**:
- ✅ 播放开始时录音按钮变绿色
- ✅ 播放结束时所有按钮恢复
- ✅ 播放错误时所有按钮恢复

**修改位置**:
- `synthesizeAndPlay()` 开始处
- `onended` 回调中
- 错误处理中

---

### 4.4 添加客户端回调 ⏰ 0.5小时
- [ ] 在 `app.py` 中注册客户端回调
- [ ] 验证输入框内容
- [ ] 调用状态管理器检查状态
- [ ] 返回验证结果

**验收标准**:
- ✅ 输入框为空时阻止提交
- ✅ 非空闲状态时阻止提交
- ✅ 验证通过时允许提交

**关键代码**:
```python
app.clientside_callback(
    """
    function(n_clicks, input_value) {
        if (!n_clicks) return window.dash_clientside.no_update;
        if (!input_value || !input_value.trim()) {
            console.log('输入框为空，阻止提交');
            return window.dash_clientside.no_update;
        }
        if (window.unifiedButtonStateManager) {
            const canProceed = window.unifiedButtonStateManager.handleTextButtonClick();
            if (!canProceed) return window.dash_clientside.no_update;
        }
        return n_clicks;
    }
    """,
    Output('ai-chat-x-send-btn', 'n_clicks', allow_duplicate=True),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value'),
    prevent_initial_call=True
)
```

---

## Phase 5: 后端集成 (预计2小时)

### 5.1 修改文本提交回调 ⏰ 1小时
- [ ] 修改 `callbacks/core_pages_c/chat_input_area_c.py`
- [ ] 在回调开始处验证输入框
- [ ] 输入框为空时返回 no_update
- [ ] SSE 开始时保持 busy 状态
- [ ] SSE 结束时通知前端准备 TTS

**验收标准**:
- ✅ 输入框为空时服务端拒绝处理
- ✅ SSE 流式返回时按钮保持busy
- ✅ SSE 结束时正确通知前端

**修改位置**:
```python
def handle_message_submit(...):
    # 在函数开始处添加
    if not input_value or not input_value.strip():
        log.info('输入框为空，不处理提交')
        return no_update, no_update, False, False, no_update
    
    # 原有处理逻辑...
```

---

### 5.2 SSE完成通知处理 ⏰ 1小时
- [ ] 在 SSE 流结束时发送通知
- [ ] 前端接收通知后调用 `prepareForTTS()`
- [ ] 如果启用语音自动播放则触发 TTS
- [ ] 如果未启用则直接 `resetToIdle()`

**验收标准**:
- ✅ SSE 结束后按钮状态正确
- ✅ 启用自动播放时自动触发 TTS
- ✅ 未启用时直接恢复空闲状态

**修改位置**:
- SSE 流结束处理
- TTS 触发逻辑

---

## Phase 6: 测试和优化 (预计4小时)

### 6.1 场景一测试 ⏰ 1小时
- [ ] 测试输入框为空提交
- [ ] 测试输入框有内容提交
- [ ] 测试 SSE 流式返回
- [ ] 测试 TTS 自动播放
- [ ] 测试播放中断
- [ ] 测试播放完成

**测试用例**:
1. 空输入框点击发送 → 显示警告
2. 输入内容点击发送 → 文本busy，录音灰色
3. SSE返回中 → 按钮保持状态
4. SSE结束 → 录音按钮变黄色
5. TTS开始 → 录音按钮变绿色
6. 点击停止 → 所有按钮恢复
7. 自动完成 → 所有按钮恢复

---

### 6.2 场景二测试 ⏰ 1小时
- [ ] 测试开始录音
- [ ] 测试录音中
- [ ] 测试停止录音
- [ ] 测试 STT 处理
- [ ] 测试 SSE 返回
- [ ] 测试 TTS 播放
- [ ] 测试播放完成

**测试用例**:
1. 点击录音 → 录音按钮变红色
2. 录音中 → 文本和通话按钮灰色
3. 点击停止 → 录音按钮变黄色
4. STT完成 → 文本按钮busy，录音保持黄色
5. SSE返回中 → 按钮保持状态
6. SSE结束 → 录音按钮保持黄色
7. TTS开始 → 录音按钮变绿色
8. 播放完成 → 所有按钮恢复

---

### 6.3 边界情况测试 ⏰ 1小时
- [ ] 测试快速连续点击
- [ ] 测试状态切换中点击
- [ ] 测试网络错误恢复
- [ ] 测试 STT 失败恢复
- [ ] 测试 TTS 失败恢复
- [ ] 测试页面刷新状态

**测试用例**:
1. 快速连续点击录音按钮
2. 录音中快速点击文本按钮
3. SSE断开连接
4. STT返回错误
5. TTS播放失败
6. 处理中刷新页面

---

### 6.4 性能优化 ⏰ 1小时
- [ ] 优化状态切换频率
- [ ] 减少DOM操作次数
- [ ] 优化日志输出量
- [ ] 添加状态切换防抖
- [ ] 优化按钮更新逻辑

**优化指标**:
- 状态切换延迟 < 50ms
- 按钮响应时间 < 100ms
- 内存占用 < 1MB
- CPU占用 < 5%

---

## Phase 7: 文档和清理 (预计1小时)

### 7.1 更新文档 ⏰ 0.5小时
- [ ] 更新开发文档
- [ ] 添加API文档
- [ ] 添加使用示例
- [ ] 更新测试报告

---

### 7.2 代码清理 ⏰ 0.5小时
- [ ] 移除旧的状态管理代码
- [ ] 移除调试日志
- [ ] 统一代码风格
- [ ] 添加代码注释

---

## 验收检查清单

### 功能完整性
- [ ] 场景一所有状态正确
- [ ] 场景二所有状态正确
- [ ] 输入框验证工作正常
- [ ] 按钮点击处理正确
- [ ] 错误处理完善

### 代码质量
- [ ] 代码结构清晰
- [ ] 注释完整
- [ ] 无冗余代码
- [ ] 无控制台错误
- [ ] 无控制台警告

### 用户体验
- [ ] 按钮状态切换流畅
- [ ] 视觉反馈清晰
- [ ] 错误提示友好
- [ ] 性能指标达标

### 文档完整性
- [ ] 开发文档完整
- [ ] API文档清晰
- [ ] 测试用例齐全
- [ ] 使用示例充分

---

## 风险评估

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 状态同步问题 | 中 | 高 | 使用事件驱动机制确保同步 |
| 性能问题 | 低 | 中 | 使用防抖和节流优化 |
| 兼容性问题 | 低 | 中 | 测试多种浏览器 |
| 集成冲突 | 中 | 高 | 逐步集成，充分测试 |

---

## 资源需求

- **开发人员**: 1人
- **预计工期**: 2-3天
- **测试人员**: 1人（兼职）
- **评审人员**: 1人

---

## 时间节点

| 阶段 | 开始日期 | 结束日期 | 状态 |
|------|----------|----------|------|
| Phase 1 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 2 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 3 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 4 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 5 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 6 | 待定 | 待定 | ⏸️ 待开始 |
| Phase 7 | 待定 | 待定 | ⏸️ 待开始 |

---

## 联系人

- **项目负责人**: 待定
- **技术负责人**: 待定
- **测试负责人**: 待定

---

## 备注

1. 本TODO列表会根据实际开发进度动态调整
2. 每个任务完成后需要在对应的checkbox打勾
3. 遇到问题及时更新风险评估
4. 每个Phase完成后进行阶段性评审

---

## 快速开始

### 开发环境准备
```bash
# 确保在正确的目录
cd /Users/zhangjun/PycharmProjects/yyAsistant

# 检查必要的文件
ls assets/js/voice_state_manager.js
ls assets/js/voice_recorder_enhanced.js
ls assets/js/voice_player_enhanced.js
```

### 第一个任务
从 Phase 1.1 开始：创建 `assets/js/unified_button_state_manager.js`

### 测试环境
启动前端和后端服务，在浏览器控制台测试功能

---

**最后更新**: 2025-10-15
**文档版本**: v1.0

