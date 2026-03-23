# 智能商旅助手 - 阶段验收清单

## 检查点定义

| 检查点 | 时机 | 评审内容 |
|--------|------|----------|
| **Checkpoint-A** | 每个Milestone完成 | 架构设计、技术方案 |
| **Checkpoint-B** | 每个Phase完成 | 主要功能演示 |
| **Checkpoint-C** | 集成测试完成 | 测试覆盖、缺陷修复 |
| **Checkpoint-D** | 项目完成 | 最终验收 |

---

## Phase 1: 核心架构

### Milestone 1.1: 项目结构规范化

- [ ] **目录结构**
  - [ ] `src/api/` 目录存在且结构正确
  - [ ] `src/hooks/` 目录存在且结构正确
  - [ ] `src/stores/` 目录存在且结构正确
  - [ ] `src/components/chat/` 目录存在
  - [ ] `src/components/booking/` 目录存在
  - [ ] `src/components/voice/` 目录存在
  - [ ] `src/components/cot/` 目录存在

- [ ] **路径别名配置**
  - [ ] `tsconfig.json` 中 `@/*` 别名配置正确
  - [ ] `vite.config.ts` 中路径别名配置正确
  - [ ] TypeScript 类型检查通过

- [ ] **依赖安装**
  - [ ] Zustand 已安装并可用
  - [ ] Axios 已安装并可用
  - [ ] socket.io-client 已安装并可用
  - [ ] `package.json` 已更新

### Milestone 1.2: API层开发

- [ ] **类型定义** `src/api/types.ts`
  - [ ] `ApiRequest` 接口定义
  - [ ] `ApiResponse<T>` 接口定义
  - [ ] `ChatMessage` 类型定义
  - [ ] `Session` 类型定义
  - [ ] `TransportOption` 类型定义
  - [ ] `HotelOption` 类型定义
  - [ ] `DiningOption` 类型定义
  - [ ] `ApprovalForm` 类型定义
  - [ ] `InvoiceResult` 类型定义
  - [ ] `Booking` 类型定义

- [ ] **Chat API** `src/api/endpoints/chat.ts`
  - [ ] `sendMessage` 函数实现
  - [ ] `getChatHistory` 函数实现
  - [ ] `createSession` 函数实现

- [ ] **Intent API** `src/api/endpoints/intent.ts`
  - [ ] `parseIntent` 函数实现
  - [ ] `submitClarification` 函数实现

- [ ] **Transport API** `src/api/endpoints/transport.ts`
  - [ ] `searchTransport` 函数实现
  - [ ] `bookTransport` 函数实现

- [ ] **Hotel API** `src/api/endpoints/hotel.ts`
  - [ ] `searchHotel` 函数实现
  - [ ] `bookHotel` 函数实现

- [ ] **Dining API** `src/api/endpoints/dining.ts`
  - [ ] `searchDining` 函数实现
  - [ ] `reserveDining` 函数实现

- [ ] **Approval API** `src/api/endpoints/approval.ts`
  - [ ] `generateApproval` 函数实现
  - [ ] `getApproval` 函数实现
  - [ ] `exportApprovalPDF` 函数实现

- [ ] **Invoice API** `src/api/endpoints/invoice.ts`
  - [ ] `uploadInvoice` 函数实现
  - [ ] `confirmInvoice` 函数实现

- [ ] **Booking API** `src/api/endpoints/booking.ts`
  - [ ] `getBookingList` 函数实现
  - [ ] `cancelBooking` 函数实现

- [ ] **API Hooks** `src/hooks/useApi.ts`
  - [ ] `useSendMessage` Hook
  - [ ] `useSearchTransport` Hook
  - [ ] `useSearchHotel` Hook
  - [ ] `useSearchDining` Hook

### Milestone 1.3: 状态管理层开发

- [ ] **ChatStore** `src/stores/chatStore.ts`
  - [ ] State 定义完整 (sessionId, messages, context, workflowStatus)
  - [ ] `sendMessage` Action 实现
  - [ ] `loadHistory` Action 实现
  - [ ] `updateContext` Action 实现
  - [ ] `setWorkflowStatus` Action 实现
  - [ ] TypeScript 类型正确

- [ ] **AgentStore** `src/stores/agentStore.ts`
  - [ ] State 定义完整 (activeAgents, agentResults)
  - [ ] `startAgent` Action 实现
  - [ ] `updateAgentProgress` Action 实现
  - [ ] `setAgentResult` Action 实现
  - [ ] `completeAgent` Action 实现
  - [ ] `failAgent` Action 实现

- [ ] **BookingStore** `src/stores/bookingStore.ts`
  - [ ] State 定义完整 (bookings, currentBooking)
  - [ ] `createBooking` Action 实现
  - [ ] `cancelBooking` Action 实现
  - [ ] `loadBookings` Action 实现

- [ ] **Store集成**
  - [ ] App.tsx 中 Provider 设置正确
  - [ ] Store 之间无循环依赖
  - [ ] DevTools 可用（Zustand）

### Milestone 1.4: WebSocket服务开发

- [ ] **连接管理** `src/hooks/useWebSocket.ts`
  - [ ] 连接建立逻辑正确
  - [ ] 连接关闭逻辑正确
  - [ ] 自动重连机制实现
  - [ ] 心跳检测实现

- [ ] **消息分发**
  - [ ] `new_message` 类型处理
  - [ ] `agent_progress` 类型处理
  - [ ] `intent_update` 类型处理
  - [ ] `clarification_req` 类型处理
  - [ ] `booking_result` 类型处理
  - [ ] `error` 类型处理

- [ ] **集成测试**
  - [ ] 与 ChatStore 集成正常
  - [ ] 消息接收正常
  - [ ] 状态更新正常

---

## Phase 2: 核心交互流程

### Milestone 2.1: 意图理解与追问流程

- [ ] **ClarificationPrompt组件**
  - [ ] UI 符合设计规范
  - [ ] 支持多问题展示
  - [ ] 问题文本显示正确

- [ ] **QuestionInput组件**
  - [ ] 文本输入支持
  - [ ] 选项输入支持
  - [ ] 答案回调正确

- [ ] **IntentProgress组件**
  - [ ] 进度百分比计算正确
  - [ ] 已收集字段显示正确
  - [ ] 缺失字段显示正确

- [ ] **追问流程集成**
  - [ ] 追问触发条件正确
  - [ ] 答案提交流程正确
  - [ ] 进度更新正确

### Milestone 2.2: 出行方案推荐流程

- [ ] **TransportSearchForm组件**
  - [ ] 出发地/目的地输入
  - [ ] 日期选择
  - [ ] 出行类型选择（飞机/火车）
  - [ ] 搜索按钮功能正常

- [ ] **TransportOptionCard组件**
  - [ ] 航班/火车信息展示
  - [ ] 时间/价格/历时展示
  - [ ] 合规性标识
  - [ ] 选择/预订按钮

- [ ] **TransportComparison组件**
  - [ ] 多方案并排展示
  - [ ] 差异高亮

- [ ] **BookingConfirmDialog组件**
  - [ ] 预订信息确认
  - [ ] 确认/取消按钮
  - [ ] 预订结果处理

### Milestone 2.3: 酒店推荐流程

- [ ] **HotelSearchForm组件**
  - [ ] 城市/日期/星级筛选
  - [ ] 搜索功能正常

- [ ] **HotelCard组件**
  - [ ] 酒店名称/星级/价格
  - [ ] 距离信息
  - [ ] 设施标签
  - [ ] 合规性标识

- [ ] **HotelDetailSheet组件**
  - [ ] 酒店详情侧边栏
  - [ ] 图片展示
  - [ ] 完整信息展示
  - [ ] 预订入口

- [ ] **DualRecommendation组件**
  - [ ] 合规推荐区
  - [ ] 超标替代区
  - [ ] 切换逻辑正确

### Milestone 2.4: 宴请推荐流程

- [ ] **DiningSearchForm组件**
  - [ ] 城市/日期/人数
  - [ ] 菜系选择
  - [ ] 搜索功能正常

- [ ] **RestaurantCard组件**
  - [ ] 餐厅名称/菜系/评分
  - [ ] 人均价格
  - [ ] 包间标识
  - [ ] 推荐菜品

- [ ] **DishRecommendation组件**
  - [ ] 菜品列表
  - [ ] 适合人数
  - [ ] 价格信息

- [ ] **DiningPlanSummary组件**
  - [ ] 餐厅汇总
  - [ ] 总花费
  - [ ] 菜品建议

---

## Phase 3: 审批与发票

### Milestone 3.1: 审批单生成流程

- [ ] **ApprovalSummary组件**
  - [ ] 基本信息展示
  - [ ] 行程信息展示
  - [ ] 汇总展示

- [ ] **ExpenseBreakdown组件**
  - [ ] 费用分类正确
  - [ ] 小计/合计正确
  - [ ] 费用明细完整

- [ ] **ComplianceComparison组件**
  - [ ] 差标对比正确
  - [ ] 超标金额高亮
  - [ ] 替代建议

- [ ] **ApprovalExport组件**
  - [ ] PDF导出功能
  - [ ] 导出进度
  - [ ] 下载成功提示

### Milestone 3.2: 发票识别流程

- [ ] **InvoiceUploader组件**
  - [ ] 拖拽上传
  - [ ] 点击上传
  - [ ] 批量上传
  - [ ] 上传进度

- [ ] **InvoicePreview组件**
  - [ ] 图片预览
  - [ ] PDF预览
  - [ ] 缩放功能

- [ ] **InvoiceFieldEditor组件**
  - [ ] 字段显示
  - [ ] 低置信度标记
  - [ ] 字段编辑
  - [ ] 确认功能

- [ ] **InvoiceBatchList组件**
  - [ ] 发票列表
  - [ ] 状态筛选
  - [ ] 批量操作

---

## Phase 4: 语音交互

### Milestone 4.1: TTS集成

- [ ] **AudioPlayer组件**
  - [ ] 音频播放
  - [ ] 暂停/继续
  - [ ] 停止
  - [ ] 进度显示
  - [ ] 音量控制

- [ ] **VoiceControlBar组件**
  - [ ] 控制按钮
  - [ ] 状态显示
  - [ ] 音量调节

- [ ] **TTS Hook**
  - [ ] 流式音频接收
  - [ ] 自动播放
  - [ ] 错误处理

### Milestone 4.2: ASR集成

- [ ] **RecordingIndicator组件**
  - [ ] 录音状态
  - [ ] 时长显示
  - [ ] 可视化

- [ ] **ASR Hook**
  - [ ] 录音采集
  - [ ] 流式上传
  - [ ] 实时识别
  - [ ] 结果回调

- [ ] **实时识别展示**
  - [ ] 文本显示
  - [ ] 断句处理
  - [ ] 编辑支持

### Milestone 4.3: 数字人动画

- [ ] **DigitalAvatar组件**
  - [ ] 头像显示
  - [ ] 状态切换
  - [ ] 动画流畅

- [ ] **状态动画系统**
  - [ ] 聆听状态
  - [ ] 思考状态
  - [ ] 说话状态
  - [ ] 待机状态

- [ ] **Agent协作动画**
  - [ ] 多角色切换
  - [ ] 协作指示

---

## Phase 5: COT展示

### Milestone 5.1: 思维链可视化

- [ ] **COTExplorer组件**
  - [ ] 四层结构展示
  - [ ] 层级切换
  - [ ] 展开/折叠

- [ ] **COTLayerView组件**
  - [ ] 层级标题
  - [ ] 内容展示
  - [ ] 图标标识

- [ ] **COTStepCard组件**
  - [ ] 步骤编号
  - [ ] 推理内容
  - [ ] 置信度

### Milestone 5.2: Agent状态追踪

- [ ] **AgentStatusBar组件**
  - [ ] Agent列表
  - [ ] 状态图标
  - [ ] 进度显示

- [ ] **AgentProgressList组件**
  - [ ] 进度列表
  - [ ] 状态筛选
  - [ ] 详情展开

- [ ] **WorkflowDiagram组件**
  - [ ] 工作流图
  - [ ] 节点状态
  - [ ] 连线动画

---

## Phase 6: 订单管理

### Milestone 6.1: 预订功能

- [ ] **BookingDrawer组件**
  - [ ] 侧边栏展示
  - [ ] 订单详情
  - [ ] 操作按钮

- [ ] **OrderStatusBadge组件**
  - [ ] 待确认状态
  - [ ] 已确认状态
  - [ ] 已取消状态

- [ ] **CancelBookingDialog组件**
  - [ ] 取消确认
  - [ ] 取消原因
  - [ ] 确认/取消按钮

### Milestone 6.2: 订单历史

- [ ] **OrderHistoryList组件**
  - [ ] 订单列表
  - [ ] 订单筛选
  - [ ] 分页加载

- [ ] **OrderFilters组件**
  - [ ] 日期筛选
  - [ ] 状态筛选
  - [ ] 类型筛选

- [ ] **OrderDetailView组件**
  - [ ] 订单详情
  - [ ] 操作记录
  - [ ] 再次预订

---

## Phase 7: 集成优化

### Milestone 7.1: 系统集成

- [ ] **前后端联调**
  - [ ] 所有API对接成功
  - [ ] 数据格式正确
  - [ ] 错误处理正常

- [ ] **WebSocket联调**
  - [ ] 消息收发正常
  - [ ] 重连机制正常
  - [ ] 心跳正常

- [ ] **全流程测试**
  - [ ] 出行规划流程
  - [ ] 酒店预订流程
  - [ ] 宴请安排流程
  - [ ] 审批单生成流程
  - [ ] 发票识别流程

### Milestone 7.2: 性能优化

- [ ] **组件懒加载**
  - [ ] 路由懒加载
  - [ ] 组件懒加载
  - [ ] 首屏加载<2s

- [ ] **虚拟列表**
  - [ ] 长列表虚拟滚动
  - [ ] 性能提升明显

- [ ] **缓存优化**
  - [ ] React Query缓存策略
  - [ ] 重复请求减少

- [ ] **Bundle优化**
  - [ ] 构建产物<500KB
  - [ ] 代码分割合理

### Milestone 7.3: UI/UX优化

- [ ] **响应式完善**
  - [ ] 移动端适配
  - [ ] 平板适配
  - [ ] 桌面适配

- [ ] **动画优化**
  - [ ] 过渡动画流畅
  - [ ] 无卡顿

- [ ] **错误处理**
  - [ ] ErrorBoundary
  - [ ] 错误提示友好
  - [ ] 错误日志

- [ ] **空状态**
  - [ ] 各空状态完善
  - [ ] 引导用户操作

---

## 最终验收检查点 D

- [ ] **功能完整性**
  - [ ] 所有设计功能已实现
  - [ ] 用户流程无断点
  - [ ] 异常流程已处理

- [ ] **代码质量**
  - [ ] TypeScript类型完整
  - [ ] ESLint无错误
  - [ ] 代码可读性良好

- [ ] **测试覆盖**
  - [ ] 单元测试覆盖率达标
  - [ ] 集成测试通过
  - [ ] E2E测试通过

- [ ] **性能达标**
  - [ ] 首屏加载<2s
  - [ ] 交互响应<100ms
  - [ ] 内存占用合理

- [ ] **文档完整**
  - [ ] README更新
  - [ ] API文档完整
  - [ ] 部署文档完整

---

**版本**: v1.0
**更新日期**: 2026-03-22
**维护者**: ProjectManager Agent