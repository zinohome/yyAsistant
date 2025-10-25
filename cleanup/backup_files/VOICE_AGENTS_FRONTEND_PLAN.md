# YYAssistant Voice Agents 前端实施计划

**项目**: YYAssistant 语音助手前端实施计划  
**版本**: v1.0  
**日期**: 2025年1月  
**目标**: 在现有yyAsistant前端基础上实现完整的语音交互功能

---

## 📋 项目概述

### 目标
将yyAsistant从纯文本聊天界面升级为支持语音交互的智能助手前端，包括：
- 语音输入界面和录音功能
- 语音输出播放和音频管理
- 实时语音对话界面
- 与现有UI组件的无缝集成

### 技术架构
```
用户界面 → 语音组件 → WebSocket → yychat后端 → 音频响应 → 播放组件
```

---

## 🎯 实施阶段

### 阶段1：基础语音组件（2-3周）

#### 1.1 语音输入组件
**目标**: 实现语音录制和识别功能

**任务清单**:
- [ ] 创建语音输入组件
  ```python
  # components/voice_input.py
  import dash
  from dash import html, dcc, callback, Input, Output, State
  import feffery_antd_components as fac
  import feffery_utils_components as fuc
  
  class VoiceInputComponent:
      def __init__(self):
          self.recording = False
          self.audio_chunks = []
          self.media_recorder = None
      
      def render(self):
          return html.Div([
              # 语音输入按钮
              fac.AntdButton(
                  id="voice-input-btn",
                  type="primary",
                  icon="microphone",
                  children="按住说话",
                  style={"width": "100%", "height": "50px"}
              ),
              
              # 录音状态指示器
              html.Div(
                  id="recording-indicator",
                  style={"display": "none"},
                  children=[
                      fac.AntdSpin(
                          children="正在录音...",
                          size="small"
                      )
                  ]
              ),
              
              # 隐藏的音频元素
              html.Audio(id="audio-player", controls=False),
              
              # 隐藏的录音数据存储
              dcc.Store(id="audio-data-store"),
              
              # WebSocket连接
              dcc.Store(id="websocket-connection-store")
          ])
  ```

- [ ] 实现录音功能
  ```javascript
  // assets/js/voice_recorder.js
  class VoiceRecorder {
      constructor() {
          this.mediaRecorder = null;
          this.audioChunks = [];
          this.isRecording = false;
      }
      
      async startRecording() {
          try {
              const stream = await navigator.mediaDevices.getUserMedia({ 
                  audio: {
                      sampleRate: 16000,
                      channelCount: 1,
                      echoCancellation: true,
                      noiseSuppression: true
                  } 
              });
              
              this.mediaRecorder = new MediaRecorder(stream, {
                  mimeType: 'audio/webm;codecs=opus'
              });
              
              this.audioChunks = [];
              this.mediaRecorder.ondataavailable = (event) => {
                  this.audioChunks.push(event.data);
              };
              
              this.mediaRecorder.onstop = () => {
                  const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                  this.processAudio(audioBlob);
              };
              
              this.mediaRecorder.start();
              this.isRecording = true;
              
          } catch (error) {
              console.error('录音启动失败:', error);
          }
      }
      
      stopRecording() {
          if (this.mediaRecorder && this.isRecording) {
              this.mediaRecorder.stop();
              this.isRecording = false;
          }
      }
      
      processAudio(audioBlob) {
          // 转换为base64并发送到后端
          const reader = new FileReader();
          reader.onload = () => {
              const base64Audio = reader.result.split(',')[1];
              this.sendAudioToBackend(base64Audio);
          };
          reader.readAsDataURL(audioBlob);
      }
  }
  ```

- [ ] 添加语音输入回调
  ```python
  # callbacks/voice_input_c.py
  @app.callback(
      [Output("recording-indicator", "style"),
       Output("voice-input-btn", "children")],
      [Input("voice-input-btn", "n_clicks")],
      [State("recording-indicator", "style")]
  )
  def toggle_recording(n_clicks, current_style):
      if n_clicks and n_clicks % 2 == 1:
          # 开始录音
          return {"display": "block"}, "松开结束"
      else:
          # 停止录音
          return {"display": "none"}, "按住说话"
  ```

#### 1.2 语音输出组件
**目标**: 实现语音播放功能

**任务清单**:
- [ ] 创建语音输出组件
  ```python
  # components/voice_output.py
  class VoiceOutputComponent:
      def __init__(self):
          self.audio_queue = []
          self.is_playing = False
      
      def render(self):
          return html.Div([
              # 语音播放控制
              fac.AntdButton(
                  id="voice-play-btn",
                  type="default",
                  icon="sound",
                  children="播放语音",
                  style={"margin": "5px"}
              ),
              
              # 语音播放进度
              fac.AntdProgress(
                  id="voice-progress",
                  percent=0,
                  showInfo=False,
                  style={"display": "none"}
              ),
              
              # 音频播放器
              html.Audio(
                  id="voice-audio-player",
                  controls=True,
                  style={"width": "100%", "display": "none"}
              ),
              
              # 音频数据存储
              dcc.Store(id="voice-audio-store"),
              
              # 播放状态存储
              dcc.Store(id="voice-playing-store", data=False)
          ])
  ```

- [ ] 实现音频播放功能
  ```javascript
  // assets/js/voice_player.js
  class VoicePlayer {
      constructor() {
          this.audioElement = document.getElementById('voice-audio-player');
          this.isPlaying = false;
          this.audioQueue = [];
      }
      
      playAudio(audioData) {
          // 创建音频URL
          const audioBlob = this.base64ToBlob(audioData, 'audio/mpeg');
          const audioUrl = URL.createObjectURL(audioBlob);
          
          // 设置音频源
          this.audioElement.src = audioUrl;
          
          // 播放音频
          this.audioElement.play().then(() => {
              this.isPlaying = true;
              this.updatePlayButton();
          }).catch(error => {
              console.error('音频播放失败:', error);
          });
          
          // 监听播放结束
          this.audioElement.onended = () => {
              this.isPlaying = false;
              this.updatePlayButton();
              URL.revokeObjectURL(audioUrl);
          };
      }
      
      updatePlayButton() {
          const button = document.getElementById('voice-play-btn');
          if (this.isPlaying) {
              button.innerHTML = '⏸️ 暂停';
          } else {
              button.innerHTML = '🔊 播放';
          }
      }
  }
  ```

#### 1.3 WebSocket连接管理
**目标**: 建立与yychat后端的实时连接

**任务清单**:
- [ ] 创建WebSocket管理器
  ```javascript
  // assets/js/websocket_manager.js
  class WebSocketManager {
      constructor() {
          this.ws = null;
          this.reconnectAttempts = 0;
          this.maxReconnectAttempts = 5;
          this.reconnectInterval = 1000;
      }
      
      connect() {
          const wsUrl = `ws://localhost:9800/ws/chat`;
          this.ws = new WebSocket(wsUrl);
          
          this.ws.onopen = () => {
              console.log('WebSocket连接已建立');
              this.reconnectAttempts = 0;
          };
          
          this.ws.onmessage = (event) => {
              this.handleMessage(JSON.parse(event.data));
          };
          
          this.ws.onclose = () => {
              console.log('WebSocket连接已关闭');
              this.attemptReconnect();
          };
          
          this.ws.onerror = (error) => {
              console.error('WebSocket错误:', error);
          };
      }
      
      sendMessage(message) {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
              this.ws.send(JSON.stringify(message));
          }
      }
      
      handleMessage(data) {
          const messageType = data.type;
          
          switch (messageType) {
              case 'text_response':
                  this.handleTextResponse(data);
                  break;
              case 'audio_response':
                  this.handleAudioResponse(data);
                  break;
              case 'transcription_complete':
                  this.handleTranscriptionComplete(data);
                  break;
              case 'error':
                  this.handleError(data);
                  break;
          }
      }
  }
  ```

- [ ] 集成到现有聊天界面
  ```python
  # callbacks/websocket_c.py
  @app.callback(
      Output("chat-messages", "children"),
      [Input("websocket-connection-store", "data")],
      [State("chat-messages", "children")]
  )
  def handle_websocket_message(ws_data, current_messages):
      if ws_data and ws_data.get("type") == "text_response":
          # 添加文本消息到聊天界面
          new_message = create_chat_message(
              content=ws_data["data"]["content"],
              role="assistant"
          )
          return current_messages + [new_message]
      
      return current_messages
  ```

### 阶段2：实时语音对话（2-3周）

#### 2.1 实时音频流处理
**目标**: 实现真正的实时语音对话

**任务清单**:
- [ ] 实现实时音频流
  ```javascript
  // assets/js/realtime_audio.js
  class RealtimeAudioProcessor {
      constructor() {
          this.audioContext = null;
          this.mediaStream = null;
          this.processor = null;
          this.isProcessing = false;
      }
      
      async startRealtimeMode() {
          try {
              // 创建音频上下文
              this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
              
              // 获取麦克风权限
              this.mediaStream = await navigator.mediaDevices.getUserMedia({
                  audio: {
                      sampleRate: 16000,
                      channelCount: 1,
                      echoCancellation: true,
                      noiseSuppression: true
                  }
              });
              
              // 创建音频处理器
              const source = this.audioContext.createMediaStreamSource(this.mediaStream);
              this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
              
              this.processor.onaudioprocess = (event) => {
                  if (this.isProcessing) {
                      const audioData = event.inputBuffer.getChannelData(0);
                      this.processAudioChunk(audioData);
                  }
              };
              
              source.connect(this.processor);
              this.processor.connect(this.audioContext.destination);
              
              this.isProcessing = true;
              
          } catch (error) {
              console.error('实时音频处理启动失败:', error);
          }
      }
      
      processAudioChunk(audioData) {
          // 检测语音活动
          if (this.detectSpeechActivity(audioData)) {
              // 发送音频数据到后端
              this.sendAudioChunk(audioData);
          }
      }
      
      detectSpeechActivity(audioData) {
          // 简单的音量检测
          const rms = Math.sqrt(
              audioData.reduce((sum, sample) => sum + sample * sample, 0) / audioData.length
          );
          return rms > 0.01; // 阈值可调整
      }
  }
  ```

- [ ] 实现语音活动检测
  ```javascript
  // assets/js/voice_activity_detection.js
  class VoiceActivityDetector {
      constructor() {
          this.silenceThreshold = 0.01;
          this.silenceDuration = 1000; // ms
          this.lastSpeechTime = 0;
          this.isSpeaking = false;
      }
      
      detectSpeech(audioData) {
          const rms = this.calculateRMS(audioData);
          const currentTime = Date.now();
          
          if (rms > this.silenceThreshold) {
              this.lastSpeechTime = currentTime;
              if (!this.isSpeaking) {
                  this.isSpeaking = true;
                  this.onSpeechStart();
              }
          } else if (currentTime - this.lastSpeechTime > this.silenceDuration) {
              if (this.isSpeaking) {
                  this.isSpeaking = false;
                  this.onSpeechEnd();
              }
          }
          
          return this.isSpeaking;
      }
      
      calculateRMS(audioData) {
          let sum = 0;
          for (let i = 0; i < audioData.length; i++) {
              sum += audioData[i] * audioData[i];
          }
          return Math.sqrt(sum / audioData.length);
      }
  }
  ```

#### 2.2 实时UI更新
**目标**: 实现流畅的实时交互界面

**任务清单**:
- [ ] 创建实时对话界面
  ```python
  # components/realtime_voice_chat.py
  class RealtimeVoiceChatComponent:
      def render(self):
          return html.Div([
              # 实时对话控制面板
              fac.AntdCard([
                  fac.AntdRow([
                      fac.AntdCol([
                          fac.AntdButton(
                              id="realtime-start-btn",
                              type="primary",
                              icon="microphone",
                              children="开始实时对话",
                              size="large"
                          )
                      ], span=8),
                      fac.AntdCol([
                          fac.AntdButton(
                              id="realtime-stop-btn",
                              type="default",
                              icon="stop",
                              children="停止对话",
                              size="large",
                              disabled=True
                          )
                      ], span=8),
                      fac.AntdCol([
                          fac.AntdButton(
                              id="realtime-mute-btn",
                              type="default",
                              icon="sound",
                              children="静音",
                              size="large"
                          )
                      ], span=8)
                  ]),
                  
                  # 实时状态指示器
                  html.Div([
                      fac.AntdBadge(
                          dot=True,
                          color="red",
                          children="正在监听"
                      ),
                      html.Span(" 实时语音对话模式", style={"marginLeft": "10px"})
                  ], id="realtime-status", style={"marginTop": "10px"})
                  
              ], title="实时语音对话"),
              
              # 对话历史
              html.Div(id="realtime-chat-history"),
              
              # 音频可视化
              html.Canvas(
                  id="audio-visualizer",
                  width=400,
                  height=100,
                  style={"border": "1px solid #ccc", "marginTop": "10px"}
              )
          ])
  ```

- [ ] 实现音频可视化
  ```javascript
  // assets/js/audio_visualizer.js
  class AudioVisualizer {
      constructor(canvasId) {
          this.canvas = document.getElementById(canvasId);
          this.ctx = this.canvas.getContext('2d');
          this.animationId = null;
      }
      
      startVisualization(audioData) {
          const draw = () => {
              this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
              
              // 绘制音频波形
              this.ctx.beginPath();
              this.ctx.moveTo(0, this.canvas.height / 2);
              
              for (let i = 0; i < audioData.length; i++) {
                  const x = (i / audioData.length) * this.canvas.width;
                  const y = (audioData[i] * this.canvas.height / 2) + (this.canvas.height / 2);
                  this.ctx.lineTo(x, y);
              }
              
              this.ctx.strokeStyle = '#1890ff';
              this.ctx.lineWidth = 2;
              this.ctx.stroke();
              
              this.animationId = requestAnimationFrame(draw);
          };
          
          draw();
      }
      
      stopVisualization() {
          if (this.animationId) {
              cancelAnimationFrame(this.animationId);
              this.animationId = null;
          }
      }
  }
  ```

#### 2.3 与现有聊天界面集成
**目标**: 无缝集成到现有聊天功能

**任务清单**:
- [ ] 修改现有聊天输入组件
  ```python
  # components/chat_input_area.py (修改)
  def render_chat_input_with_voice():
      return html.Div([
          # 现有的文本输入
          fac.AntdInput.TextArea(
              id="chat-input",
              placeholder="输入消息或点击语音按钮...",
              autoSize={"minRows": 1, "maxRows": 4}
          ),
          
          # 语音输入按钮
          fac.AntdButton(
              id="voice-input-toggle",
              type="text",
              icon="microphone",
              style={"marginLeft": "5px"}
          ),
          
          # 发送按钮
          fac.AntdButton(
              id="send-button",
              type="primary",
              icon="send"
          ),
          
          # 语音模式切换
          fac.AntdSwitch(
              id="voice-mode-switch",
              checkedChildren="语音",
              unCheckedChildren="文本"
          )
      ], style={"display": "flex", "alignItems": "flex-end"})
  ```

- [ ] 更新聊天消息显示
  ```python
  # components/chat_message.py (修改)
  def create_voice_message(content, role, audio_data=None):
      message_components = [
          # 文本内容
          html.Div(content, className="message-content"),
      ]
      
      # 如果有音频数据，添加播放按钮
      if audio_data:
          message_components.append(
              fac.AntdButton(
                  type="text",
                  icon="sound",
                  children="播放",
                  onClick=f"playAudio('{audio_data}')"
              )
          )
      
      return html.Div(
          message_components,
          className=f"message {role}-message"
      )
  ```

### 阶段3：高级功能集成（2-3周）

#### 3.1 语音设置和个性化
**目标**: 实现语音个性化功能

**任务清单**:
- [ ] 创建语音设置组件
  ```python
  # components/voice_settings.py
  class VoiceSettingsComponent:
      def render(self):
          return fac.AntdDrawer([
              fac.AntdTitle("语音设置", level=4),
              
              # 语音选择
              fac.AntdFormItem([
                  fac.AntdText("选择语音"),
                  fac.AntdSelect(
                      id="voice-select",
                      options=[
                          {"label": "Alloy (中性)", "value": "alloy"},
                          {"label": "Echo (男性)", "value": "echo"},
                          {"label": "Fable (女性)", "value": "fable"},
                          {"label": "Onyx (男性)", "value": "onyx"},
                          {"label": "Nova (女性)", "value": "nova"},
                          {"label": "Shimmer (女性)", "value": "shimmer"}
                      ],
                      defaultValue="alloy"
                  )
              ]),
              
              # 语速设置
              fac.AntdFormItem([
                  fac.AntdText("语速"),
                  fac.AntdSlider(
                      id="speech-rate",
                      min=0.5,
                      max=2.0,
                      step=0.1,
                      defaultValue=1.0,
                      marks={0.5: "慢", 1.0: "正常", 2.0: "快"}
                  )
              ]),
              
              # 音量设置
              fac.AntdFormItem([
                  fac.AntdText("音量"),
                  fac.AntdSlider(
                      id="speech-volume",
                      min=0,
                      max=100,
                      defaultValue=80,
                      marks={0: "静音", 50: "中等", 100: "最大"}
                  )
              ]),
              
              # 自动播放设置
              fac.AntdFormItem([
                  fac.AntdSwitch(
                      id="auto-play-switch",
                      checkedChildren="开启",
                      unCheckedChildren="关闭",
                      children="自动播放语音回复"
                  )
              ])
              
          ], id="voice-settings-drawer", title="语音设置")
  ```

- [ ] 实现语音个性化
  ```python
  # callbacks/voice_personalization_c.py
  @app.callback(
      Output("voice-settings-store", "data"),
      [Input("voice-select", "value"),
       Input("speech-rate", "value"),
       Input("speech-volume", "value"),
       Input("auto-play-switch", "checked")]
  )
  def update_voice_settings(voice, rate, volume, auto_play):
      return {
          "voice": voice,
          "rate": rate,
          "volume": volume,
          "auto_play": auto_play
      }
  ```

#### 3.2 错误处理和用户反馈
**目标**: 提供良好的错误处理和用户反馈

**任务清单**:
- [ ] 实现错误处理
  ```python
  # components/error_handler.py
  class VoiceErrorHandler:
      @staticmethod
      def show_error(error_type, message):
          return fac.AntdNotification.Notification(
              message="语音功能错误",
              description=message,
              type="error",
              duration=5
          )
      
      @staticmethod
      def show_success(message):
          return fac.AntdNotification.Notification(
              message="操作成功",
              description=message,
              type="success",
              duration=3
          )
  ```

- [ ] 添加用户引导
  ```python
  # components/voice_tutorial.py
  class VoiceTutorialComponent:
      def render(self):
          return fac.AntdModal([
              fac.AntdTitle("语音功能使用指南", level=4),
              
              html.Div([
                  fac.AntdSteps([
                      fac.AntdStepsItem(
                          title="启用麦克风",
                          description="点击麦克风按钮，允许浏览器访问您的麦克风"
                      ),
                      fac.AntdStepsItem(
                          title="开始录音",
                          description="按住麦克风按钮开始录音，松开结束录音"
                      ),
                      fac.AntdStepsItem(
                          title="播放回复",
                          description="AI的回复会自动播放，您也可以手动点击播放按钮"
                      )
                  ])
              ])
              
          ], id="voice-tutorial-modal", title="语音功能指南")
  ```

#### 3.3 性能优化
**目标**: 优化语音功能的性能

**任务清单**:
- [ ] 实现音频缓存
  ```javascript
  // assets/js/audio_cache.js
  class AudioCache {
      constructor() {
          this.cache = new Map();
          this.maxSize = 50; // 最大缓存数量
      }
      
      set(key, audioData) {
          if (this.cache.size >= this.maxSize) {
              // 删除最旧的缓存
              const firstKey = this.cache.keys().next().value;
              this.cache.delete(firstKey);
          }
          this.cache.set(key, audioData);
      }
      
      get(key) {
          return this.cache.get(key);
      }
      
      has(key) {
          return this.cache.has(key);
      }
  }
  ```

- [ ] 实现音频压缩
  ```javascript
  // assets/js/audio_compression.js
  class AudioCompressor {
      static compressAudio(audioBlob) {
          // 使用Web Audio API压缩音频
          return new Promise((resolve) => {
              const audioContext = new AudioContext();
              const fileReader = new FileReader();
              
              fileReader.onload = () => {
                  audioContext.decodeAudioData(fileReader.result).then(audioBuffer => {
                      // 压缩处理
                      const compressedBlob = this.processAudioBuffer(audioBuffer);
                      resolve(compressedBlob);
                  });
              };
              
              fileReader.readAsArrayBuffer(audioBlob);
          });
      }
  }
  ```

### 阶段4：测试和优化（1-2周）

#### 4.1 功能测试
**目标**: 确保语音功能正常工作

**任务清单**:
- [ ] 单元测试
  ```python
  # tests/test_voice_components.py
  def test_voice_input_component():
      # 测试语音输入组件
      pass
  
  def test_voice_output_component():
      # 测试语音输出组件
      pass
  
  def test_websocket_connection():
      # 测试WebSocket连接
      pass
  ```

- [ ] 集成测试
  ```python
  # tests/test_voice_integration.py
  def test_voice_chat_flow():
      # 测试完整的语音聊天流程
      pass
  
  def test_realtime_voice_chat():
      # 测试实时语音对话
      pass
  ```

#### 4.2 性能测试
**目标**: 确保语音功能性能良好

**任务清单**:
- [ ] 延迟测试
  ```javascript
  // 测试语音处理延迟
  class PerformanceTester {
      static testVoiceLatency() {
          const startTime = performance.now();
          // 执行语音处理
          const endTime = performance.now();
          console.log(`语音处理延迟: ${endTime - startTime}ms`);
      }
  }
  ```

- [ ] 内存使用测试
  ```javascript
  // 测试内存使用情况
  class MemoryTester {
      static checkMemoryUsage() {
          if (performance.memory) {
              console.log(`内存使用: ${performance.memory.usedJSHeapSize / 1024 / 1024}MB`);
          }
      }
  }
  ```

---

## 🔧 技术实现细节

### 依赖管理
```python
# requirements.txt 新增依赖
dash-extensions>=0.1.0
websockets>=11.0.3
```

### 静态资源
```javascript
// assets/js/voice_agents.js (主入口文件)
import { VoiceRecorder } from './voice_recorder.js';
import { VoicePlayer } from './voice_player.js';
import { WebSocketManager } from './websocket_manager.js';
import { RealtimeAudioProcessor } from './realtime_audio.js';

// 初始化语音功能
document.addEventListener('DOMContentLoaded', () => {
    const voiceRecorder = new VoiceRecorder();
    const voicePlayer = new VoicePlayer();
    const wsManager = new WebSocketManager();
    const realtimeProcessor = new RealtimeAudioProcessor();
    
    // 绑定事件
    bindVoiceEvents(voiceRecorder, voicePlayer, wsManager, realtimeProcessor);
});
```

### 配置管理
```python
# configs/voice_config.py
class VoiceConfig:
    # WebSocket配置
    WS_URL = "ws://localhost:9800/ws/chat"
    WS_RECONNECT_INTERVAL = 1000
    WS_MAX_RECONNECT_ATTEMPTS = 5
    
    # 音频配置
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_BIT_RATE = 128000
    
    # 语音活动检测
    VAD_THRESHOLD = 0.01
    VAD_SILENCE_DURATION = 1000
    
    # UI配置
    AUTO_PLAY_DEFAULT = True
    VOICE_DEFAULT = "alloy"
    VOLUME_DEFAULT = 80
```

---

## 📊 性能指标

### 目标性能
- **录音延迟**: < 100ms
- **播放延迟**: < 200ms
- **WebSocket延迟**: < 50ms
- **内存使用**: < 100MB

### 监控指标
- 语音处理成功率
- 音频播放质量
- WebSocket连接稳定性
- 用户交互响应时间

---

## 🚀 部署计划

### 开发环境
1. 本地开发测试
2. 浏览器兼容性测试
3. 移动端适配测试

### 生产环境
1. CDN配置（音频文件）
2. WebSocket负载均衡
3. 音频缓存策略

---

## 📝 风险评估

### 技术风险
- **浏览器兼容性**: 不同浏览器的音频API支持差异
- **网络延迟**: 影响实时语音交互体验
- **音频质量**: 网络条件影响音频传输质量

### 缓解措施
- 实现多浏览器兼容性检测
- 使用音频压缩减少传输量
- 实现音频质量自适应

---

## 🎯 成功标准

### 功能完整性
- [ ] 支持语音输入识别
- [ ] 支持语音输出播放
- [ ] 支持实时语音对话
- [ ] 与现有UI完美集成

### 性能标准
- [ ] 录音延迟 < 100ms
- [ ] 播放延迟 < 200ms
- [ ] 支持主流浏览器
- [ ] 移动端适配良好

### 用户体验
- [ ] 语音交互自然流畅
- [ ] 错误处理友好
- [ ] 界面直观易用
- [ ] 设置灵活多样

---

**实施负责人**: 前端开发团队  
**预计完成时间**: 8-11周  
**资源需求**: 2名前端开发人员，1名UI/UX设计师
