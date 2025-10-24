组件与模式清单（基于 Feffery 系列）

布局与导航

- `fuc.FefferyDiv`：统一容器，使用 `scrollbar/shadow/style` 属性
- `fac.AntdRow/Col/Space/Affix`：响应式布局与吸附
- `fac.AntdMenu`：基于 `RouterConfig.core_side_menu` 渲染，配合 `TreeManager` 做权限裁剪
- `fuc.FefferyLocation`：URL 监听；`dcc.Location` 用于全局跳转

表单与输入

- 登录页：`AntdForm/AntdInput/AntdButton/AntdCheckbox` + `FefferyMotion` 动效
- 聊天输入：`AntdInput` 多行、发送按钮、附件/语音占位，使用 `style()` 保持一致视觉

消息渲染

- 用户消息：`AntdAvatar + AntdText` 包装在 `FefferyDiv` 中
- AI/代理消息：`fmc.FefferyMarkdown` 渲染富文本，外层 `FefferyDiv` 控制滚动与阴影
- 操作栏：`AntdIcon`/`DashIconify` 提供复制/赞踩等入口

全局反馈

- `fuc.FefferyTopProgress`：回调运行时顶栏进度
- `fac.Fragment` + `set_props`：全局消息、重定向、刷新、下载

样式与工具

- 统一使用 `feffery_dash_utils.style_utils.style` 生成内联样式
- `TreeManager` 用于菜单/树节点增删改
- 版本校验：`version_utils` 保证依赖版本安全

最佳实践

- 回调中尽量返回 `dash.no_update` 避免不必要刷新
- 通过 `running` 控制进度动画，`on_error` 统一错误渲染
- SSE 更新 DOM 时，优先更新 `FefferyMarkdown` 内容而非直接 `textContent`（已在客户端回调兼容）


组件关系简图（Mermaid）

```mermaid
flowchart LR
  SideMenu[core_side_menu] -->|权限裁剪| AntdMenu
  ChatInput[chat_input_area] --> Store[(ai-chat-x-messages-store)]
  Store --> SSE[chat-X-sse]
  SSE --> AgentMsg[ChatAgentMessage(FMC)]
  UserMsg[ChatUserMessage(FAC)] --> Store
```

示例截图（登录表单）：

![登录表单](/assets/imgs/logo.svg)
