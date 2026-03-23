# 智能商旅助手 - 多Agent协同开发框架

## 1. 框架概述

本文档定义了智能商旅助手前端开发的多Agent协同框架，通过专业化分工和系统化流程，实现复杂项目的有序推进。

### 1.1 核心原则

- **专业分工**：每个Agent负责特定领域，避免职责混乱
- **渐进式开发**：从核心架构到业务功能，逐步迭代
- **可追溯性**：每个决策和变更都有明确记录
- **自文档化**：代码即文档，通过类型和注释保持清晰

### 1.2 Agent角色矩阵

| Agent | 职责 | 触发条件 |
|-------|------|----------|
| **ProjectManager** | 任务分解、进度跟踪、风险识别 | 项目开始、遇到阻塞 |
| **Architect** | 技术方案设计、架构决策、技术选型 | 进入新阶段、需要技术决策 |
| **ComponentDev** | UI组件开发、业务逻辑实现 | 需要开发具体功能 |
| **APIDev** | API接口定义、前后端联调 | 需要接口开发或联调 |
| **TestEngineer** | 测试用例编写、测试覆盖 | 功能开发完成 |
| **CodeReviewer** | 代码质量审查、最佳实践 | 代码提交前 |
| **Documenter** | 文档编写、技术沉淀 | 需要文档记录 |

## 2. 开发阶段定义

### 阶段划分

```
Phase 1: 核心架构 (Week 1-2)
├── M1.1: 项目结构规范化
├── M1.2: API层开发
├── M1.3: 状态管理层开发
└── M1.4: WebSocket服务开发

Phase 2: 核心交互流程 (Week 3-4)
├── M2.1: 意图理解与追问流程
├── M2.2: 出行方案推荐流程
├── M2.3: 酒店推荐流程
└── M2.4: 宴请推荐流程

Phase 3: 审批与发票 (Week 5)
├── M3.1: 审批单生成流程
└── M3.2: 发票识别流程

Phase 4: 语音交互 (Week 6)
├── M4.1: TTS集成
├── M4.2: ASR集成
└── M4.3: 数字人动画

Phase 5: COT展示 (Week 7)
├── M5.1: 思维链可视化
└── M5.2: Agent状态追踪

Phase 6: 订单管理 (Week 8)
├── M6.1: 预订功能
└── M6.2: 订单历史

Phase 7: 集成优化 (Week 9-10)
├── M7.1: 系统集成
├── M7.2: 性能优化
└── M7.3: UI/UX优化
```

## 3. 任务执行标准

### 3.1 任务创建标准

每个任务必须包含：
```yaml
task_id: string          # 唯一标识 (e.g., "P1-M1.1-T001")
title: string            # 简洁标题
description: string      # 详细描述
acceptance_criteria:     # 验收标准列表
  - criterion: string
    verification: string # 验证方法
dependencies: []         # 前置任务
assignee: Agent          # 负责Agent
status: pending          # 状态
priority: high/medium/low
estimated_hours: number
actual_hours: number     # 完成时记录
```

### 3.2 任务执行流程

```
创建任务 → 确认依赖 → 执行开发 → 自测验证 → 代码审查 → 任务关闭
    ↓           ↓           ↓           ↓           ↓
  检查前置    编码实现    单元测试    审查意见    合并代码
```

### 3.3 检查点机制

每个Milestone设置检查点：
- **CheckPoint-A**: 架构评审（进入下一阶段前）
- **CheckPoint-B**: 功能演示（主要功能完成）
- **CheckPoint-C**: 测试通过（测试覆盖达标）
- **CheckPoint-D**: 最终验收（所有标准达成）

## 4. 代码规范

### 4.1 目录结构

```
src/
├── api/                    # API调用层
│   ├── client.ts          # Axios实例
│   ├── interceptors.ts   # 拦截器
│   ├── endpoints/         # 分模块API
│   │   ├── chat.ts
│   │   ├── intent.ts
│   │   ├── transport.ts
│   │   ├── hotel.ts
│   │   ├── dining.ts
│   │   ├── approval.ts
│   │   └── invoice.ts
│   └── types.ts
├── hooks/                  # 自定义Hooks
│   ├── useChat.ts
│   ├── useWebSocket.ts
│   ├── useBooking.ts
│   └── useVoice.ts
├── stores/                 # 状态管理
│   ├── chatStore.ts
│   ├── agentStore.ts
│   └── bookingStore.ts
├── components/
│   ├── chat/
│   ├── booking/
│   ├── voice/
│   ├── cot/
│   └── ui/
├── pages/
├── lib/
└── types/
```

### 4.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `ChatPage.tsx` |
| Hooks | camelCase, use前缀 | `useChat.ts` |
| Store | camelCase, Store后缀 | `chatStore.ts` |
| API函数 | camelCase,动词优先 | `sendMessage` |
| 类型/接口 | PascalCase, 可选I前缀 | `ChatMessage` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| CSS类 | kebab-case | `chat-container` |

### 4.3 组件开发标准

```typescript
// 1. 组件文件结构
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

// Types
interface ComponentNameProps {
  className?: string;
  onAction?: (value: string) => void;
}

// Component
export function ComponentName({ className, onAction }: ComponentNameProps) {
  const [state, setState] = useState<string>('');

  const handleAction = useCallback(() => {
    onAction?.(state);
  }, [state, onAction]);

  return (
    <div className={cn('base-classes', className)}>
      {/* content */}
    </div>
  );
}
```

## 5. API设计规范

### 5.1 REST API规范

```typescript
// 请求格式
interface ApiRequest<T = any> {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: T;
  params?: Record<string, string>;
  headers?: Record<string, string>;
}

// 响应格式
interface ApiResponse<T = any> {
  code: number;      // 0 = success, 非0 = error
  message: string;
  data: T;
  timestamp: number;
}
```

### 5.2 WebSocket消息规范

```typescript
// 客户端 → 服务端
interface WSClientMessage {
  type: 'send_message' | 'subscribe' | 'unsubscribe';
  payload: any;
  session_id: string;
}

// 服务端 → 客户端
interface WSServerMessage {
  type: 'new_message' | 'agent_progress' | 'intent_update' | 'booking_result' | 'error';
  payload: any;
  timestamp: number;
}
```

## 6. 质量标准

### 6.1 测试覆盖率要求

| 层级 | 最低覆盖率 |
|------|-----------|
| Hooks | 80% |
| 工具函数 | 90% |
| 业务组件 | 60% |
| 页面组件 | 40% |

### 6.2 代码质量标准

- **TypeScript**: 严格模式，无any类型
- **ESLint**: 无错误（Error），警告（Warning）≤10
- **复杂度**: 函数圈复杂度 ≤ 15
- **行数**: 单文件 ≤ 500行，单函数 ≤ 100行

### 6.3 性能标准

| 指标 | 目标值 |
|------|--------|
| 首屏加载 | < 2s |
| API响应 | < 500ms |
| WebSocket延迟 | < 200ms |
| 交互响应 | < 100ms |
| 组件重渲染 | 60fps |

## 7. 协同流程

### 7.1 每日协同

```
Morning: 任务分配 → Agent各自执行
Mid-day: 进度同步 → 阻塞处理
Evening: 结果汇总 → 问题记录
```

### 7.2 阶段协同

```
Architect: 设计技术方案 → ComponentDev: 实现
                                    ↓
                            APIDev: 接口联调
                                    ↓
                         TestEngineer: 测试验证
                                    ↓
                        CodeReviewer: 质量审查
                                    ↓
                         Documenter: 文档更新
```

## 8. 风险管理

### 8.1 风险识别

| 风险 | 影响 | 概率 | 应对 |
|------|------|------|------|
| 后端API延迟 | 高 | 中 | Mock数据降级 |
| WebSocket断连 | 中 | 低 | 自动重连机制 |
| 多Agent状态同步 | 高 | 中 | 统一状态管理 |
| 复杂交互流程 | 中 | 高 | 分步实现，逐步集成 |

### 8.2 降级策略

```
完全正常 → WebSocket降级轮询 → Mock数据响应 → 静态页面
```

## 9. 文档管理

### 9.1 必需文档

- `SKILL.md` - Agent技能定义
- `TASKS.md` - 任务分解清单
- `CHECKLIST.md` - 阶段验收清单
- `CHANGELOG.md` - 变更记录

### 9.2 文档更新时机

- 新增功能 → 更新TASKS.md
- 架构变更 → 更新设计文档
- 阶段完成 → 更新CHECKLIST.md
- 代码变更 → 更新CHANGELOG.md

---

**版本**: v1.0
**更新日期**: 2026-03-22
**维护者**: ProjectManager Agent