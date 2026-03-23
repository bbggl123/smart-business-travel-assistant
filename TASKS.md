# 智能商旅助手 - 开发任务分解清单（后端优先版）

## 项目信息

- **项目名称**: 智能商旅助手
- **前端路径**: `c:\Users\Administrator\Downloads\digital-dialogue-hub-main`
- **后端路径**: `c:\Users\Administrator\Downloads\digital-dialogue-hub-main\backend`
- **前端技术栈**: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **后端技术栈**: Python + FastAPI + Supabase (PostgreSQL + Redis)
- **LLM**: 紫东太初 Kimi-K2.5

---

## ⚠️ 开发策略说明

**后端优先策略**：
1. 先完整开发后端（Phase B + Phase C + Phase D）
2. 测试验证后端 API
3. 再开发前端（Phase A + Phase E + Phase F + Phase G）
4. 最后集成测试（Phase G）

**优势**：
- 后端 API 确定后，前端开发有明确标准
- 避免接口变更导致的前端返工
- 可以通过 API 文档和 Mock Server 验证业务逻辑

---

## Phase B: 后端基础设施 (Week 1)

### Milestone B.1: 后端项目初始化

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| B1-T001 | 创建后端目录结构 | 按照 plan.md 创建 backend/ 目录结构 | high | 2 |
| B1-T002 | 配置 Python 环境 | 创建虚拟环境，安装依赖 | high | 2 |
| B1-T003 | 配置 Supabase 连接 | 实现 Supabase PostgreSQL + Redis 客户端 | high | 3 |
| B1-T004 | 配置日志系统 | 实现统一日志工具 | medium | 1 |

**验收标准**:
- [ ] backend/ 目录结构符合 plan.md
- [ ] requirements.txt 包含所有依赖
- [ ] Supabase 连接测试通过

---

### Milestone B.2: LLM 网关开发

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| B2-T001 | 实现 Provider 抽象层 | 定义 LLM Provider 接口 | high | 2 |
| B2-T002 | 实现紫东太初 Provider | 集成紫东太初 Kimi-K2.5 API | high | 4 |
| B2-T003 | 实现统一网关 | 封装调用接口，支持流式响应 | high | 3 |
| B2-T004 | 实现错误处理和重试 | 失败重试、限流、超时处理 | high | 2 |

**验收标准**:
- [ ] 紫东太初 API 调用成功
- [ ] 流式响应正常工作
- [ ] 错误处理和重试机制正常

---

### Milestone B.3: 数据库模型

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| B3-T001 | 实现 User 模型 | 用户表 CRUD | high | 2 |
| B3-T002 | 实现 Session 模型 | 会话表 CRUD | high | 2 |
| B3-T003 | 实现 Message 模型 | 消息表 CRUD | high | 2 |
| B3-T004 | 实现 Trip 模型 | 出差计划表 CRUD | high | 2 |
| B3-T005 | 实现 Booking 模型 | 订单表 CRUD | high | 2 |

**验收标准**:
- [ ] 所有数据库模型创建成功
- [ ] CRUD 操作正常
- [ ] 与 Supabase 连接正常

---

## Phase C: Agent 开发 (Week 2-3)

### Milestone C.1: Dispatcher Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C1-T001 | 实现消息接收 | 接收用户消息，判断请求类型 | high | 3 |
| C1-T002 | 实现工作流创建 | 根据请求类型创建工作流 | high | 4 |
| C1-T003 | 实现任务分发 | 分发任务到专业 Agent | high | 3 |
| C1-T004 | 实现结果聚合 | 聚合多 Agent 结果 | high | 3 |

**验收标准**:
- [ ] 能正确识别请求类型
- [ ] 工作流创建正确
- [ ] 任务分发正常

---

### Milestone C.2: Intent Understanding Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C2-T001 | 实现语义解析 | 解析用户自然语言输入 | high | 4 |
| C2-T002 | 实现意图分类 | 判断用户意图类型 | high | 3 |
| C2-T003 | 实现信息提取 | 提取结构化信息 | high | 3 |
| C2-T004 | 实现追问生成 | 生成追问问题列表 | high | 3 |
| C2-T005 | 实现上下文管理 | 管理会话上下文 | high | 3 |

**验收标准**:
- [ ] 语义解析正确
- [ ] 意图分类准确
- [ ] 追问生成合理

---

### Milestone C.3: Transportation Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C3-T001 | 实现航班搜索 | 搜索航班信息（Mock） | high | 3 |
| C3-T002 | 实现火车搜索 | 搜索火车票信息（Mock） | high | 3 |
| C3-T003 | 实现方案推荐 | 生成出行推荐报告 | high | 3 |
| C3-T004 | 实现预订功能 | Mock 预订机票/火车票 | medium | 3 |

**验收标准**:
- [ ] 航班搜索返回结果
- [ ] 火车搜索返回结果
- [ ] 推荐报告生成正确

---

### Milestone C.4: Hotel Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C4-T001 | 实现酒店搜索 | 搜索酒店信息（Mock） | high | 3 |
| C4-T002 | 实现距离计算 | 计算酒店与客户位置距离 | medium | 2 |
| C4-T003 | 实现双重推荐 | 合规推荐 + 替代方案 | high | 3 |
| C4-T004 | 实现预订功能 | Mock 预订酒店 | medium | 2 |

**验收标准**:
- [ ] 酒店搜索返回结果
- [ ] 双重推荐逻辑正确
- [ ] 预订功能正常

---

### Milestone C.5: Dining Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C5-T001 | 实现餐厅搜索 | 搜索餐厅信息（Mock） | high | 3 |
| C5-T002 | 实现菜品推荐 | 推荐匹配宴请人数的菜品 | high | 3 |
| C5-T003 | 实现双重展示 | 超标提示 + 合规推荐 | high | 3 |
| C5-T004 | 实现预约功能 | Mock 预约餐厅 | medium | 2 |

**验收标准**:
- [ ] 餐厅搜索返回结果
- [ ] 菜品推荐合理
- [ ] 双重展示正确

---

### Milestone C.6: Compliance Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| C6-T001 | 实现规则引擎 | 维护差旅标准规则库 | high | 4 |
| C6-T002 | 实现交通合规检查 | 验证飞机/火车费用 | high | 3 |
| C6-T003 | 实现住宿合规检查 | 验证酒店费用 | high | 3 |
| C6-T004 | 实现餐饮合规检查 | 验证宴请人均费用 | high | 3 |
| C6-T005 | 生成合规报告 | 输出结构化合规报告 | high | 2 |

**验收标准**:
- [ ] 规则引擎正确
- [ ] 合规检查准确
- [ ] 报告生成正确

---

## Phase D: 审批与发票 (Week 4)

### Milestone D.1: Approval Form Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| D1-T001 | 实现数据汇总 | 汇总各 Agent 推荐结果 | high | 3 |
| D1-T002 | 实现审批单生成 | 生成审批单 HTML | high | 4 |
| D1-T003 | 实现 PDF 导出 | HTML 转 PDF | medium | 3 |
| D1-T004 | 实现打印支持 | 打印功能 | low | 1 |

**验收标准**:
- [ ] 数据汇总正确
- [ ] 审批单格式正确
- [ ] PDF 导出正常

---

### Milestone D.2: Invoice Agent

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| D2-T001 | 实现发票上传 | 支持图片/PDF 上传 | high | 3 |
| D2-T002 | 实现 OCR 识别 | 调用紫东太初多模态识别 | high | 4 |
| D2-T003 | 实现字段提取 | 提取发票字段 | high | 3 |
| D2-T004 | 实现批量处理 | 支持多张发票 | medium | 2 |

**验收标准**:
- [ ] 上传功能正常
- [ ] OCR 识别准确
- [ ] 批量处理正常

---

## Phase B-C-D: 后端 API 测试 (Week 4-5)

### Milestone BCD-TEST: 后端完整测试

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| TEST-001 | API 接口测试 | 测试所有 REST API | high | 8 |
| TEST-002 | WebSocket 测试 | 测试实时通信 | high | 4 |
| TEST-003 | Agent 协作测试 | 测试多 Agent 协作流程 | high | 8 |
| TEST-004 | Mock 数据验证 | 验证 Mock 数据正确性 | medium | 4 |

**验收标准**:
- [ ] 所有 API 接口测试通过
- [ ] WebSocket 通信正常
- [ ] 多 Agent 协作流程正常
- [ ] Mock 数据符合预期

---

## Phase A: 前端核心架构 (Week 5-6)

*前提条件：Phase B + Phase C + Phase D + 测试全部完成*

### Milestone A.1: 项目结构规范化

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| A1-T001 | 安装前端依赖 | 引入Zustand、Axios、socket.io-client | high | 2 |
| A1-T002 | 创建目录结构 | 按照框架规范创建src下的目录结构 | high | 2 |
| A1-T003 | 配置路径别名 | 配置tsconfig和vite的路径别名 | high | 1 |
| A1-T004 | 创建 .env 配置 | 配置后端API地址 | high | 1 |

**验收标准**:
- [ ] 目录结构符合规范
- [ ] `@/` 路径别名可用
- [ ] 依赖安装成功

---

### Milestone A.2: API 层开发

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| A2-T001 | 定义 API 类型 | 创建 `src/api/types.ts` 定义所有类型 | high | 3 |
| A2-T002 | 实现 API Client | 创建 Axios 实例和拦截器 | high | 2 |
| A2-T003 | 实现 Chat API | 创建 `src/api/endpoints/chat.ts` | high | 3 |
| A2-T004 | 实现 Intent API | 创建 `src/api/endpoints/intent.ts` | high | 3 |
| A2-T005 | 实现 Transport/Hotel/Dining API | 各模块 API | high | 6 |
| A2-T006 | 实现 Approval/Invoice/Booking API | 各模块 API | high | 6 |

**验收标准**:
- [ ] 所有 API 类型定义完整
- [ ] API endpoint 函数实现
- [ ] 与后端联调通过

---

### Milestone A.3: 状态管理层开发

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| A3-T001 | 设计 ChatStore | 对话状态管理 | high | 4 |
| A3-T002 | 设计 AgentStore | Agent 状态管理 | high | 4 |
| A3-T003 | 设计 BookingStore | 订单状态管理 | high | 3 |
| A3-T004 | 集成 Store | 在 App.tsx 中集成所有 Store | high | 2 |

**验收标准**:
- [ ] ChatStore 功能完整
- [ ] AgentStore 功能完整
- [ ] BookingStore 功能完整

---

### Milestone A.4: WebSocket 服务开发

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| A4-T001 | 实现连接管理 | WebSocket 连接管理 Hook | high | 4 |
| A4-T002 | 实现消息分发 | 消息类型分发逻辑 | high | 3 |
| A4-T003 | 实现心跳重连 | 心跳检测和断线重连 | high | 3 |
| A4-T004 | 集成到 ChatStore | 将 WebSocket 集成到状态管理 | high | 3 |

**验收标准**:
- [ ] WebSocket 连接正常
- [ ] 消息分发正确
- [ ] 断线自动重连

---

## Phase E: 前端交互流程 (Week 6-7)

### Milestone E.1: 意图理解与追问流程

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| E1-T001 | ClarificationPrompt 组件 | 追问提示组件 | high | 3 |
| E1-T002 | QuestionInput 组件 | 问题回答输入组件 | high | 3 |
| E1-T003 | IntentProgress 组件 | 意图收集进度指示器 | medium | 2 |
| E1-T004 | 追问流程集成 | 将追问流程集成到 ChatPage | high | 4 |

**验收标准**:
- [ ] 追问组件 UI 美观
- [ ] 支持文本和选项输入
- [ ] 进度指示器准确

---

### Milestone E.2: 出行方案推荐流程

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| E2-T001 | TransportSearchForm 组件 | 出行搜索表单 | high | 3 |
| E2-T002 | TransportOptionCard 组件 | 出行方案卡片 | high | 4 |
| E2-T003 | BookingConfirmDialog 组件 | 预订确认对话框 | high | 3 |
| E2-T004 | 出行流程集成 | 集成到 ChatPage | high | 4 |

**验收标准**:
- [ ] 搜索表单功能完整
- [ ] 卡片展示信息完整
- [ ] 预订确认流程顺畅

---

### Milestone E.3: 酒店/宴请流程

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| E3-T001 | HotelCard/DiningCard 组件 | 酒店/餐厅卡片 | high | 4 |
| E3-T002 | DualRecommendation 组件 | 双重推荐展示 | high | 4 |
| E3-T003 | 酒店/宴请流程集成 | 集成到 ChatPage | high | 4 |

**验收标准**:
- [ ] 卡片展示完整
- [ ] 双重推荐正确
- [ ] 流程集成正常

---

## Phase F: COT 展示 (Week 7)

### Milestone F.1: 思维链可视化

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| F1-T001 | COTExplorer 组件 | 思维链浏览器 | high | 5 |
| F1-T002 | COTLayerView 组件 | 单层推理结果展示 | high | 4 |
| F1-T003 | COTStepCard 组件 | 推理步骤卡片 | medium | 3 |

**验收标准**:
- [ ] 四层结构展示清晰
- [ ] 支持展开折叠
- [ ] 调试模式可用

---

### Milestone F.2: Agent 状态追踪

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| F2-T001 | AgentStatusBar 组件 | Agent 状态栏 | high | 4 |
| F2-T002 | AgentProgressList 组件 | Agent 进度列表 | high | 3 |
| F2-T003 | WorkflowDiagram 组件 | 工作流状态图 | medium | 4 |

**验收标准**:
- [ ] 状态显示准确
- [ ] 进度更新及时
- [ ] 工作流图清晰

---

## Phase G: 集成与优化 (Week 8)

### Milestone G.1: 系统集成

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| G1-T001 | 前后端联调 | 与后端 API 联调 | high | 8 |
| G1-T002 | WebSocket 联调 | WebSocket 实时通信测试 | high | 4 |
| G1-T003 | 全流程测试 | 完整业务流程测试 | high | 6 |

**验收标准**:
- [ ] 所有 API 对接正常
- [ ] WebSocket 稳定
- [ ] 全流程无阻塞

---

### Milestone G.2: 性能优化

| Task ID | Title | Description | Priority | Est.Hours |
|---------|-------|-------------|----------|-----------|
| G2-T001 | 组件懒加载 | 实现路由级懒加载 | medium | 3 |
| G2-T002 | 缓存优化 | 合理使用缓存策略 | medium | 3 |
| G2-T003 | Bundle 优化 | 优化构建产物大小 | medium | 2 |

**验收标准**:
- [ ] 首屏加载 < 2s
- [ ] Bundle < 500KB
- [ ] 无明显性能问题

---

## 任务统计（后端优先版）

| Phase | 任务数 | 预计工时 | 前提条件 |
|-------|--------|----------|----------|
| Phase B: 后端基础设施 | 14 | 40h | 无 |
| Phase C: Agent 开发 | 24 | 70h | Phase B 完成 |
| Phase D: 审批与发票 | 8 | 20h | Phase C 完成 |
| Phase B-C-D 测试 | 4 | 24h | Phase D 完成 |
| Phase A: 前端核心架构 | 17 | 45h | Phase B-C-D 测试完成 |
| Phase E: 前端交互流程 | 10 | 30h | Phase A 完成 |
| Phase F: COT 展示 | 6 | 20h | Phase E 完成 |
| Phase G: 集成与优化 | 6 | 20h | Phase F 完成 |
| **总计** | **89** | **269h** | - |

---

## 执行记录

| 日期 | Phase | 执行任务 | 完成情况 | 备注 |
|------|-------|----------|----------|------|
| 2026-03-22 | - | 创建任务分解清单（后端优先版） | ✅ 完成 | 采用后端优先策略 |

---

## 下一步行动（后端优先）

### Week 1: Phase B - 后端基础设施
```
Day 1-2: 后端项目初始化
├── 创建 backend/ 目录结构
├── 配置 Python 环境，安装依赖
├── 配置 Supabase 连接
└── 配置日志系统

Day 3-5: LLM 网关开发
├── 实现 Provider 抽象层
├── 实现紫东太初 Provider
├── 实现统一网关
└── 实现错误处理和重试

Day 6-8: 数据库模型
├── 实现 User/Session/Message 模型
├── 实现 Trip/Booking 模型
└── Supabase 连接测试
```

### Week 2-3: Phase C - Agent 开发
```
Day 9-12: Dispatcher + Intent Agent
├── 实现消息接收
├── 实现工作流创建
├── 实现语义解析
└── 实现意图分类

Day 13-16: Transportation/Hotel/Dining Agent
├── 实现航班/火车搜索（Mock）
├── 实现酒店搜索（Mock）
├── 实现餐厅搜索（Mock）
└── 实现预订功能（Mock）

Day 17-20: Compliance Agent
├── 实现规则引擎
├── 实现交通/住宿/餐饮合规检查
└── 生成合规报告
```

### Week 4: Phase D - 审批与发票 + 测试
```
Day 21-24: 审批与发票
├── 实现 Approval Form Agent
├── 实现 Invoice Agent
└── 测试后端 API
```

### Week 5-8: Phase A-F - 前端开发
```
Day 25-30: 前端核心架构
Day 31-36: 前端交互流程
Day 37-40: COT 展示
Day 41-48: 集成与优化
```

---

**版本**: v3.0 (后端优先版)
**更新日期**: 2026-03-22
**维护者**: ProjectManager Agent