# 语音实时对话文本显示功能 - 快速测试指南

## 🚀 快速开始测试

### 步骤1：启动服务

1. **启动后端服务**（yychat项目）
   ```bash
   cd /Users/zhangjun/CursorProjects/yychat
   python app.py
   # 或
   uvicorn app:app --host 0.0.0.0 --port 9800
   ```

2. **启动前端服务**（yyAsistant项目）
   ```bash
   cd /Users/zhangjun/CursorProjects/yyAsistant
   python app.py
   # 服务将在 http://localhost:8050 启动
   ```

### 步骤2：打开浏览器测试

1. 访问：http://localhost:8050
2. 登录系统
3. 进入 `/core/chat` 页面
4. 打开浏览器开发者工具（F12），查看控制台日志

## ✅ 核心功能测试

### 测试1：录音聊天（验证场景区分）

**操作**：
1. 点击录音按钮开始录音
2. 说话后停止录音
3. 观察聊天历史

**预期结果**：
- ✅ 转录文本出现在聊天历史中
- ✅ 悬浮面板不显示（因为场景是 `voice_recording`）
- ✅ 控制台日志显示："收到录音聊天转录结果，跳过语音实时对话处理"

### 测试2：语音实时对话（核心功能）

**操作**：
1. 点击"开始实时对话"按钮（语音通话按钮）
2. 观察悬浮面板是否出现（应在聊天历史上方）
3. 说话后观察文本是否实时显示
4. 停止对话
5. 观察悬浮面板是否隐藏

**预期结果**：
- ✅ 对话开始时，悬浮面板显示（`voice-call-text-display`）
- ✅ 转录文本实时显示在悬浮面板中（整句显示，非流式）
- ✅ 用户消息显示为蓝色（👤 用户）
- ✅ AI回复显示为绿色（🤖 AI）
- ✅ 每条消息显示时间戳
- ✅ 对话停止后，悬浮面板隐藏
- ✅ 控制台日志显示："收到语音实时对话转录结果"

### 测试3：关闭按钮

**操作**：
1. 开始语音实时对话
2. 点击悬浮面板右上角的关闭按钮（❌）
3. 观察面板是否隐藏

**预期结果**：
- ✅ 点击关闭按钮后，面板隐藏（`display: none`）
- ✅ 对话继续正常进行（不影响功能）

### 测试4：场景切换

**操作**：
1. 先进行一次录音聊天
2. 然后进行一次语音实时对话
3. 再回到录音聊天
4. 观察消息是否正确分离

**预期结果**：
- ✅ 录音聊天的消息只出现在聊天历史中
- ✅ 语音实时对话的消息只出现在悬浮面板中
- ✅ 两种场景的消息不混淆
- ✅ 控制台日志正确区分场景类型

## 🔍 检查清单

### 前端检查

打开浏览器开发者工具（F12），检查：

- [ ] **控制台无JavaScript错误**
  - 查看Console标签，应无红色错误信息
  
- [ ] **Store正确更新**
  - 在Console中输入：`window.dash_clientside.set_props('voice-call-transcription-display', {data: {messages: [], is_active: false}})`
  - 观察Store是否更新
  
- [ ] **UI元素存在**
  - 在Console中输入：`document.getElementById('voice-call-text-display')`
  - 应返回DOM元素（不为null）
  - 在Console中输入：`document.getElementById('voice-call-text-content')`
  - 应返回DOM元素（不为null）

- [ ] **配置项正确加载**
  - 在Console中输入：`window.voiceConfig`
  - 应显示包含以下字段的对象：
    - `VOICE_CALL_SHOW_TRANSCRIPTION`
    - `VOICE_CALL_SAVE_TO_DATABASE`
    - `VOICE_CALL_MAX_DISPLAY_MESSAGES`
    - `VOICE_CALL_TRANSCRIPTION_DEBOUNCE`

### 后端检查

查看后端日志（yychat项目），检查：

- [ ] **服务器日志无错误**
  - 查看日志，应无错误信息
  
- [ ] **WebSocket连接正常**
  - 查看日志，应显示连接成功信息
  
- [ ] **场景字段正确设置**
  - 查看日志，`transcription_result` 消息应包含 `scenario` 字段：
    - 录音聊天：`scenario: "voice_recording"`
    - 语音实时对话：`scenario: "voice_call"`

## 🐛 常见问题排查

### 问题1：悬浮面板不显示

**可能原因**：
1. JavaScript配置未加载
2. 场景字段未正确设置
3. CSS样式问题

**解决方法**：
1. 检查浏览器控制台是否有错误
2. 检查 `window.voiceConfig.VOICE_CALL_SHOW_TRANSCRIPTION` 是否为 `true`
3. 检查元素是否存在：`document.getElementById('voice-call-text-display')`
4. 手动显示：`document.getElementById('voice-call-text-display').style.display = 'block'`

### 问题2：文本不显示

**可能原因**：
1. WebSocket未连接
2. `client_id` 未正确获取
3. 场景字段未正确设置

**解决方法**：
1. 检查WebSocket连接状态
2. 检查控制台日志，确认收到 `transcription_result` 消息
3. 检查消息中的 `scenario` 字段是否为 `"voice_call"`
4. 检查 `handleVoiceCallTranscription` 方法是否被调用

### 问题3：场景混淆

**可能原因**：
1. 后端未正确设置场景字段
2. 前端处理器未正确区分场景

**解决方法**：
1. 检查后端日志，确认 `scenario` 字段正确设置
2. 检查前端控制台日志，确认场景区分逻辑正常
3. 检查 `voice_recorder_enhanced.js` 和 `voice_websocket_manager.js` 的场景检查逻辑

## 📊 性能检查

### 检查防抖机制

1. **快速连续说话**（在500ms内多次触发转录）
2. **观察消息更新频率**
   - 应在500ms内批量更新
   - 不应每次消息都立即更新
   - 使用浏览器Performance工具观察更新频率

### 检查消息数量限制

1. **进行超过50次对话**
2. **观察Store中的消息数量**
   - Store最多保存50条消息
   - 超出限制时，旧消息应被删除
   - UI最多显示10条消息（DOM性能优化）

## 💾 消息保存测试（可选）

### 启用保存功能

1. **修改配置**：`configs/voice_config.py`
   ```python
   VOICE_CALL_SAVE_TO_DATABASE = True
   ```

2. **重启前端服务**

3. **进行一次语音实时对话**

4. **停止对话**

5. **检查数据库**
   - 查看 `Conversations` 表
   - 确认消息已保存
   - 确认 `source` 字段为 `'voice_call'`

## 📝 测试报告

测试完成后，记录以下信息：

```
测试日期：_________
测试环境：_________
浏览器：_________

功能测试：
- [ ] 录音聊天：✅/❌
- [ ] 语音实时对话：✅/❌
- [ ] 场景切换：✅/❌
- [ ] 关闭按钮：✅/❌
- [ ] 消息保存：✅/❌

性能测试：
- [ ] 防抖机制：✅/❌
- [ ] 消息数量限制：✅/❌

发现问题：
1. _________
2. _________

测试结论：
_________
```

## 🔗 相关文档

- [开发计划](./VOICE_CALL_TEXT_DISPLAY_DEVELOPMENT_PLAN.md)
- [详细测试计划](./VOICE_CALL_TEXT_DISPLAY_TEST_PLAN.md)
- [设计方案](./VOICE_CALL_TEXT_DISPLAY_PLAN.md)

